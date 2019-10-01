import k8s_client

connect = k8s_client.k8sclient()
connect.get_pods_list()

#connect.get_component_status()
#connect.get_endpoints()
#connect.get_namespaces()
#connect.create_service("p-58mh8", "testservice", 1234)
#connect.delete_service("testservice", "p-58mh8")
connect.get_services("p-58mh8")
print('pause')