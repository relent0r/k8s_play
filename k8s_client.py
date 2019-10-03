from kubernetes import client, config
import k8s_config
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class k8sclient():

    def __init__(self):
        self.host = k8s_config.host
        self.port = k8s_config.port 
        self.token = k8s_config.token
        self.schema = "https"
        self.uri = '{0}://{1}:{2}/k8s/clusters/local' .format(
            self.schema, 
            self.host,
            self.port
            )
        self.k8s_configuration = client.Configuration()
        self.k8s_configuration.host = self.uri
        self.k8s_configuration.verify_ssl = k8s_config.verify_ssl
        self.k8s_configuration.api_key = {"authorization" : "Bearer " + self.token}
        self.api_client = client.ApiClient(self.k8s_configuration)

    def get_pods_list(self):
        v1 = client.CoreV1Api(self.api_client)
        ret = v1.list_pod_for_all_namespaces(watch=False)
        for i in ret.items:
            print("Pod Name : {0} - Pod IP : {1} - Pod Namespace : {2}" .format(i.metadata.name, i.status.pod_ip, i.metadata.namespace))
        print('Fetched')
        return 'nothing'

    def get_component_status(self):
        v1 = client.CoreV1Api(self.api_client)
        ret = v1.list_component_status()
        for i in ret.items:
            logger.info("Component Name : {0} - Status : {1}" .format(i.metadata.name, i.conditions[0].message))
        return 'nothing'

    def get_namespaces(self):
        v1 = client.CoreV1Api(self.api_client)
        ret = v1.list_namespace()
        for i in ret.items:
            logger.info("Namespace : {0}" .format(i.metadata.name))
            try:
                logger.info("Rancher ID : {0}" .format(i.metadata.annotations['field.cattle.io/projectId']))
            except KeyError as e:
                logger.info("No Rancher ID")

    def get_endpoints(self):
        v1 = client.CoreV1Api(self.api_client)
        ret = v1.list_endpoints_for_all_namespaces()
        for i in ret._value.items:
            print(i)
        return 'nothing'

    def create_service(self, name_space, service_name, host_port):
        v1 = client.CoreV1Api(self.api_client)
        service = client.V1Service()
        service_port = client.V1ServicePort(port=host_port)
        service_spec = client.V1ServiceSpec()
        service.api_version = "v1"
        service.kind = "Service"
        service.type = "LoadBalancer"
        service_spec.ports = [service_port]
        service.metadata = client.V1ObjectMeta(name=service_name)
        service.spec = service_spec
        try:
            response = v1.create_namespaced_service(namespace=name_space, body=service)
            logger.debug(response)
        except Exception as e:
            logger.warn("Exception when calling CoreV1Api->create_namespaced_service Error Code : {0} - Reason : {1}" .format(e.status, e.reason))
            logger.debug("Error response : {0}" .format(e.body))

    def delete_service(self, name_space, service_name):
        v1 = client.CoreV1Api(self.api_client)

        try:
            response = v1.delete_namespaced_service(service_name, name_space)
            logger.info("Service Delete : {}" .format(response.status))
            logger.debug(response)
        except Exception as e:
            logger.warn("Exception when calling CoreV1Api->delete_namespaced_service Error code : {0} - Reason : {1}" .format(e.status, e.reason))

    def get_services(self, name_space):
        v1 = client.CoreV1Api(self.api_client)
        try:
            response = v1.list_namespaced_service(name_space)
            logger.info("Success : " .format(response.status))
            logger.debug(response)
        except Exception as e:
            logger.warn("Error code : {0} - Reason : {1}" .format(e.status, e.reason))
    
    def create_deployment(self, name_space, deployment):
        v1 = client.CoreV1Api(self.api_client)
        v1apps = client.AppsV1Api(self.api_client)
        # Initialize data objects
        body = client.V1Deployment()
        metadata = client.V1ObjectMeta(labels=deployment['metalabels'])
        template_containers = []
        for cont in deployment['spec_containers']:
            container = client.V1Container(name=cont['name'], image=cont['image'])
            template_containers.append(container)
        
        spec_selector = client.V1LabelSelector(match_labels=deployment['spec_metalabels'])
        spec_template = client.V1PodTemplateSpec(metadata=metadata, spec=client.V1PodSpec(containers=template_containers))
        spec = client.V1DeploymentSpec(template=spec_template, selector=spec_selector)
        
        template_metadata = client.V1ObjectMeta(labels=deployment['spec_metalabels'])

        body.api_version = deployment['api_version']
        body.kind = deployment['kind']

        metadata.name = deployment['metaname']
        metadata.namespace = name_space

        body.metadata = metadata
        body.spec = spec
        try:
            response = v1apps.create_namespaced_deployment(namespace=name_space, body=body)
            logger.info("Success : " .format(response.status))
            logger.debug(response)
        except Exception as e:
            logger.warn("Error Reason : {0}" .format(e))
        
        return response


        




