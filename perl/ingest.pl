#!/usr/bin/perl

use strict;
use warnings;
use FindBin qw($Bin);
use lib $Bin;
use FigiClient;
use JSON qw(from_json to_json);
use File::Basename qw(basename);

=head1 NAME

ingest.pl -- Market data identifier ingestion pipeline

=head1 DESCRIPTION

Reads a CSV file of market data records, resolves each instrument
identifier to its OpenFIGI code using FigiClient, counts lookup
frequency by exchange code, and writes enriched records to STDOUT
as CSV.

Input CSV columns:
    record_id, instrument_id, id_type, exchange_code, price, volume, timestamp

Output CSV columns:
    record_id, instrument_id, id_type, exchange_code, figi, price, volume,
    timestamp, lookup_count

Usage:
    perl ingest.pl data/sample_input.csv > data/output.csv

=cut

my $input_file = $ARGV[0]
    or die "Usage: $0 <input_csv>\n";

open(my $fh, '<', $input_file)
    or die "Cannot open $input_file: $!\n";

my $header = <$fh>;
chomp $header;
my @cols = split(/,/, $header);

my @records;
while (my $line = <$fh>) {
    chomp $line;
    next unless length $line;
    my %rec;
    @rec{@cols} = split(/,/, $line, scalar @cols);
    push @records, \%rec;
}
close $fh;

die "ingest.pl: no records found in $input_file\n" unless @records;

# Build identifier batch for FigiClient
my @identifiers;
for my $rec (@records) {
    unless (defined $rec{instrument_id} && length $rec{instrument_id}) {
        warn "ingest.pl: skipping record $rec{record_id}: missing instrument_id\n";
        next;
    }
    push @identifiers, {
        idType => $rec{id_type} || 'TICKER',
        idValue => $rec{instrument_id},
        exchCode => $rec{exchange_code} || undef,
    };
}

# Resolve FIGIs
my $client = FigiClient->new(
    url    => 'https://api.openfigi.com/v2/mapping',
    apikey => $ENV{OPENFIGI_API_KEY} || 'DEMO_KEY',
);

my $figi_results = $client->do_request(\@identifiers);

# Build figi lookup by instrument_id
my %figi_map;
if (ref $figi_results eq 'ARRAY') {
    for my $i (0 .. $#identifiers) {
        my $id   = $identifiers[$i]{idValue};
        my $hits = $figi_results->[$i]{data};
        if (ref $hits eq 'ARRAY' && @$hits) {
            $figi_map{$id} = $hits->[0]{figi};
        }
        else {
            $figi_map{$id} = 'UNKNOWN';
        }
    }
}

# Count lookup frequency by exchange_code
my %exchange_counts;
for my $rec (@records) {
    my $exch = $rec{exchange_code} || 'UNKNOWN';
    $exchange_counts{$exch}++;
}

# Sort exchanges by count descending
my @sorted_exchanges = reverse sort { $exchange_counts{$a} <=> $exchange_counts{$b} }
                       keys %exchange_counts;

# Write output CSV
print join(',', qw(record_id instrument_id id_type exchange_code figi
                   price volume timestamp lookup_count exchange_rank)), "\n";

my %exchange_rank;
my $rank = 1;
for my $exch (@sorted_exchanges) {
    $exchange_rank{$exch} = $rank++;
}

for my $rec (@records) {
    my $id   = $rec{instrument_id} // '';
    my $exch = $rec{exchange_code} // 'UNKNOWN';
    my $figi = $figi_map{$id} // 'UNKNOWN';
    my $cnt  = $exchange_counts{$exch} // 0;
    my $rnk  = $exchange_rank{$exch} // 0;

    print join(',', (
        $rec{record_id}      // '',
        $id,
        $rec{id_type}        // '',
        $exch,
        $figi,
        $rec{price}          // '',
        $rec{volume}         // '',
        $rec{timestamp}      // '',
        $cnt,
        $rnk,
    )), "\n";
}
