# Python-time Intro

A transaction statistics profiler.

the following project is an profiler framework was writen for handle, 
manage, and get transaction response time statistics.
it also extends profilehooks, and expose some additional capabilities.

some of the advantages is the ability to publish stats to time series db.

### Advantages:
- measure response time.
- measure network IO correlated to response time.
- publish the results to time series db (influxDB).

# Quick Start

### Requirements
```
this programs require the following python dependencies:
influxdb, concurrent.futures, psutils
```

### Usage And Examples
#### setup
1. clone the project to where you want to monitor the python code.

    ```
    git clone https://github.com/mrsiano/python-time.git
    cd python-time
    # make sure your influxdb running.
    ```
2. edit the configuration file see config.cfg

    ```
    vim config.cfg
    make sure to set the influxdb: server \ port.
    make sure to specify the network device: net_device = en4
    ```
3. decorate your codes

     ```
     ./decorating_app.sh <the python code you want to monitor>
     ```


#### more standalone examples.
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

### Analysis
once your test completed and your influxdb collects the results,
import the grafana template into your grafana server.

1. first add to grafana your influxdb server.
2. make sure you change the db name in the json template file before importing.

examples:
![Alt text](screencapture-localhost-3000-dashboard-db-transactions-1484139148961.png?raw=true "Optional Title")