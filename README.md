# Python-time Intro

WIP wrap and extend profilehooks.. WIP

the following code is a framework was writen for handle, manage, 
and get transaction response time statistics.
it also extends profilehooks, and expose some additional capabilities.

some of the advantages is the ability to publish stats to influxDB.

# Quick Start

### Requirements
```
this programs require the following python dependencies:
influxdb, concurrent.futures, psutils
```

### Usage And Examples
the project includes configuration for easy usage, see config.cfg

once the configuration set, choose the right method to use in your code.
```
1. decorator usage:
    first the module should be imported e.g:
    from transResponseTime import measure_time
    
    then simply decorate functions
    
    @measure_time()
    def a_test_method(sec=0.2):
        time.sleep(sec)
        
     is it possible to use the profilehooks syntax e.g:
     @measure_time(immediate=True)
        
2. Plain usage:
    first the module should be imported e.g:
    import transResponseTime
    ...
    transResponseTime.measure('plain_usage_exam', time.sleep, 0.5)
```