#!/usr/bin/perl

use strict;
use warnings;

=head1 NAME

validate.pl -- Market data pipeline output validator

=head1 DESCRIPTION

Reads transformed CSV from transform.pl and validates each record
against the registered schema. Writes a validation report to STDOUT
and exits non-zero if any critical violations are found.

Validation rules:
    CRITICAL: record_id must be present and unique
    CRITICAL: instrument_id must be present and non-empty
    CRITICAL: price must be a positive number with exactly 4 decimal places
    CRITICAL: volume must be a positive integer
    CRITICAL: figi_resolved must be 1 (unresolved FIGIs block the pipeline)
    WARNING:  ts_valid should be 1 (invalid timestamps are logged but not fatal)
    WARNING:  notional should be greater than zero
    INFO:     size_bucket should be one of SMALL / MID / LARGE / BLOCK

Usage:
    perl transform.pl data/transformed_input.csv | perl validate.pl

Exit codes:
    0  -- all records passed, no critical violations
    1  -- one or more critical violations found

=cut

my %VALID_SIZE_BUCKETS = map { $_ => 1 } qw(SMALL MID LARGE BLOCK);

my $in = $ARGV[0] ? do { open my $f, '<', $ARGV[0] or die "$!\n"; $f } : \*STDIN;

my $header_line = <$in>;
chomp $header_line;
my @cols = split(/,/, $header_line);

my %seen_ids;
my @critical_violations;
my @warnings;
my @info;
my $record_count = 0;
my $passed_count = 0;

while (my $line = <$in>) {
    chomp $line;
    next unless length $line;

    $record_count++;
    my %rec;
    @rec{@cols} = split(/,/, $line, scalar @cols);

    my $id  = $rec{record_id} // '';
    my $row = "record_id=$id";
    my $record_ok = 1;

    # CRITICAL: record_id present and unique
    unless (length $id) {
        push @critical_violations, "$row: missing record_id";
        $record_ok = 0;
    }
    if ($seen_ids{$id}++) {
        push @critical_violations, "$row: duplicate record_id";
        $record_ok = 0;
    }

    # CRITICAL: instrument_id present
    unless (defined $rec{instrument_id} && length $rec{instrument_id}) {
        push @critical_violations, "$row: missing instrument_id";
        $record_ok = 0;
    }

    # CRITICAL: price format (positive, 4 decimal places)
    my $price = $rec{price} // '';
    unless ($price =~ /^\d+\.\d{4}$/ && $price + 0 > 0) {
        push @critical_violations,
            "$row: price '$price' is not a positive number with 4 decimal places";
        $record_ok = 0;
    }

    # CRITICAL: volume positive integer
    my $vol = $rec{volume} // '';
    unless ($vol =~ /^\d+$/ && $vol > 0) {
        push @critical_violations, "$row: volume '$vol' is not a positive integer";
        $record_ok = 0;
    }

    # CRITICAL: figi resolved
    my $figi_res = $rec{figi_resolved} // '';
    unless ($figi_res eq '1') {
        push @critical_violations, "$row: figi_resolved=0, FIGI lookup failed";
        $record_ok = 0;
    }

    # WARNING: timestamp valid
    my $ts_valid = $rec{ts_valid} // '';
    unless ($ts_valid eq '1') {
        push @warnings, "$row: ts_valid=0, timestamp format invalid";
    }

    # WARNING: notional positive
    my $notional = $rec{notional} // 0;
    unless ($notional > 0) {
        push @warnings, "$row: notional=$notional is not positive";
    }

    # INFO: size bucket known
    my $bucket = $rec{size_bucket} // '';
    unless ($VALID_SIZE_BUCKETS{$bucket}) {
        push @info, "$row: unknown size_bucket '$bucket'";
    }

    $passed_count++ if $record_ok;
}

close $in if $ARGV[0];

# Write validation report
print "=== Pipeline Validation Report ===\n";
printf "Records processed : %d\n", $record_count;
printf "Records passed    : %d\n", $passed_count;
printf "Critical violations: %d\n", scalar @critical_violations;
printf "Warnings          : %d\n", scalar @warnings;
printf "Info              : %d\n", scalar @info;
print "\n";

if (@critical_violations) {
    print "CRITICAL VIOLATIONS:\n";
    print "  $_\n" for @critical_violations;
    print "\n";
}

if (@warnings) {
    print "WARNINGS:\n";
    print "  $_\n" for @warnings;
    print "\n";
}

if (@info) {
    print "INFO:\n";
    print "  $_\n" for @info;
    print "\n";
}

my $exit_code = @critical_violations ? 1 : 0;
print @critical_violations ? "RESULT: FAIL\n" : "RESULT: PASS\n";
exit $exit_code;
