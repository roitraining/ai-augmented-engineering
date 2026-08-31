#!/usr/bin/perl

use strict;
use warnings;
use POSIX qw(floor);

=head1 NAME

transform.pl -- Market data transformation pipeline stage

=head1 DESCRIPTION

Reads enriched CSV from ingest.pl (via STDIN or file), applies
normalisation and derived field calculations, and writes transformed
records to STDOUT as CSV.

Transformations applied:
    - Normalises price to 4 decimal places
    - Calculates notional value (price * volume)
    - Classifies trade size into buckets: SMALL / MID / LARGE / BLOCK
    - Strips unknown FIGIs and flags them
    - Validates timestamp format (YYYY-MM-DD HH:MM:SS)

Input CSV must include columns from ingest.pl output.
Output adds: notional, size_bucket, figi_resolved, ts_valid

Usage:
    perl ingest.pl data/sample_input.csv | perl transform.pl > data/transformed.csv

=cut

my $BLOCK_THRESHOLD = 1_000_000;
my $LARGE_THRESHOLD =   100_000;
my $MID_THRESHOLD   =    10_000;

sub classify_size {
    my ($notional) = @_;
    return 'BLOCK' if $notional >= $BLOCK_THRESHOLD;
    return 'LARGE' if $notional >= $LARGE_THRESHOLD;
    return 'MID'   if $notional >= $MID_THRESHOLD;
    return 'SMALL';
}

sub validate_timestamp {
    my ($ts) = @_;
    return 0 unless defined $ts && length $ts;
    return 1 if $ts =~ /^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$/;
    return 0;
}

my $in = $ARGV[0] ? do { open my $f, '<', $ARGV[0] or die "$!\n"; $f } : \*STDIN;

my $header_line = <$in>;
chomp $header_line;
my @in_cols = split(/,/, $header_line);

my @out_cols = (@in_cols, qw(notional size_bucket figi_resolved ts_valid));
print join(',', @out_cols), "\n";

while (my $line = <$in>) {
    chomp $line;
    next unless length $line;

    my %rec;
    @rec{@in_cols} = split(/,/, $line, scalar @in_cols);

    # Null safety on critical numeric fields
    my $price  = defined $rec{price}  && $rec{price}  =~ /^\d/ ? $rec{price}  + 0 : undef;
    my $volume = defined $rec{volume} && $rec{volume} =~ /^\d/ ? $rec{volume} + 0 : undef;

    unless (defined $price && defined $volume) {
        warn "transform.pl: skipping record $rec{record_id}: "
           . "missing price or volume\n";
        next;
    }

    my $price_norm = sprintf("%.4f", $price);
    my $notional   = $price * $volume;
    my $size_bucket   = classify_size($notional);
    my $figi_resolved = (defined $rec{figi} && $rec{figi} ne 'UNKNOWN') ? 1 : 0;
    my $ts_valid      = validate_timestamp($rec{timestamp});

    $rec{price} = $price_norm;

    print join(',', (
        map { $rec{$_} // '' } @in_cols
    ), $notional, $size_bucket, $figi_resolved, $ts_valid), "\n";
}

close $in if $ARGV[0];
