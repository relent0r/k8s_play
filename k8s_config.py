token = 'yourtokenhere'
host = 'fqdnhostname'
port = '443'
verify_ssl = False
deployment = {
    'api_version' : 'apps/v1',
    'kind' : 'Deployment',
    'metaname' : 'centos-test-1',
    'metalabels' : {
        'app': 'centos',
        'version' : '0.5'
    },
    'spec_containers' : [
        {
            'name' : 'centostest',
            'image' : 'centos:latest'
            }
        ],
    'spec_metalabels' : {
        'app' : 'centos'
    }
}
