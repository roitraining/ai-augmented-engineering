package FigiClient;

use strict;
use warnings;
use LWP::UserAgent;
use JSON qw(from_json to_json);
use Time::HiRes qw(gettimeofday tv_interval);

=head1 NAME

FigiClient -- Client for the OpenFIGI identifier mapping API

=head1 DESCRIPTION

Maps financial instrument identifiers (ticker, ISIN, CUSIP, SEDOL)
to their OpenFIGI codes via the api.openfigi.com/v2/mapping endpoint.

Enforces a rate limit of 100 requests per 60-second window.
Retries up to 5 times on HTTP 429 (rate limited) responses.

=head1 SYNOPSIS

    my $client = FigiClient->new(
        url    => 'https://api.openfigi.com/v2/mapping',
        apikey => $ENV{OPENFIGI_API_KEY},
    );

    my $result = $client->do_request(\@identifiers);

=cut

our $VERSION = '1.0.0';

my $DEFAULT_RATE_LIMIT  = 100;
my $DEFAULT_WINDOW_SECS = 60;
my $DEFAULT_MAX_RETRIES = 5;
my $DEFAULT_RETRY_SLEEP = 2;

sub new {
    my ($class, %args) = @_;

    my $apikey = defined $args{apikey} ? $args{apikey} : $ENV{OPENFIGI_API_KEY};

    die "FigiClient: no API key provided and OPENFIGI_API_KEY not set\n"
        unless defined $apikey && length $apikey;

    my $self = {
        _url         => $args{url}         || 'https://api.openfigi.com/v2/mapping',
        _apikey      => $apikey,
        _rate_limit  => $args{rate_limit}  || $DEFAULT_RATE_LIMIT,
        _window_secs => $args{window_secs} || $DEFAULT_WINDOW_SECS,
        _max_retries => $args{max_retries} || $DEFAULT_MAX_RETRIES,
        _retry_sleep => $args{retry_sleep} || $DEFAULT_RETRY_SLEEP,
        _batch_cnt   => 0,
        _batch_start => [gettimeofday],
        _ua          => LWP::UserAgent->new(
            agent   => "FigiClient/$VERSION",
            timeout => 30,
        ),
    };

    return bless $self, $class;
}

sub do_request {
    my ($self, $identifiers) = @_;

    unless (ref $identifiers eq 'ARRAY' && @$identifiers) {
        warn "FigiClient::do_request: identifiers must be a non-empty arrayref\n";
        return undef;
    }

    # Rate limiting: enforce _rate_limit requests per _window_secs
    if ($self->{_batch_cnt} >= $self->{_rate_limit}) {
        my $elapsed = tv_interval($self->{_batch_start}, [gettimeofday]);
        if ($elapsed < $self->{_window_secs}) {
            my $sleep_for = $self->{_window_secs} - $elapsed;
            sleep($sleep_for);
        }
        $self->{_batch_cnt}   = 0;
        $self->{_batch_start} = [gettimeofday];
    }

    my $payload   = to_json($identifiers);
    my $retry     = 1;
    my $retry_cnt = 0;

    while ($retry && $retry_cnt <= $self->{_max_retries}) {
        $retry = 0;

        my $response = $self->{_ua}->post(
            $self->{_url},
            'Content-Type'      => 'application/json',
            'X-OPENFIGI-APIKEY' => $self->{_apikey},
            Content             => $payload,
        );

        my $status = $response->code;

        if ($status == 200) {
            $self->{_batch_cnt}++;
            my $data = eval { from_json($response->decoded_content, { utf8 => 1 }) };
            if ($@) {
                warn "FigiClient: failed to parse JSON response: $@\n";
                return undef;
            }
            return $data;
        }
        elsif ($status == 429) {
            $retry_cnt++;
            if ($retry_cnt <= $self->{_max_retries}) {
                warn "FigiClient: rate limited (HTTP 429), "
                   . "retry $retry_cnt of $self->{_max_retries}\n";
                sleep($self->{_retry_sleep} * $retry_cnt);
                $retry = 1;
            }
            else {
                warn "FigiClient: max retries ($self->{_max_retries}) "
                   . "exceeded on HTTP 429\n";
                return undef;
            }
        }
        else {
            warn sprintf(
                "FigiClient: unexpected HTTP %d from %s\n",
                $status, $self->{_url}
            );
            return undef;
        }
    }

    return undef;
}

1;
