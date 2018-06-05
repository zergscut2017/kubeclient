#!/usr/bin/env python3

from utils import *

from kubernetes import client, config
from kubernetes.client.rest import ApiException
from pprint import pprint
import json


class KubernetesClient:

    def __init__(self, kubernetes_admin_conf):
        config.load_kube_config(config_file=kubernetes_admin_conf)
        self.core_v1 = client.CoreV1Api()
        self.apps_v1 = client.AppsV1beta2Api()

    def find_namespace(self, namespace_name):
        v1_namespace_list = self.core_v1.list_namespace(pretty=True)
        # for i in v1_namespace_list.items:
        #     print(i.metadata.name)
        print(v1_namespace_list)
        print(type(v1_namespace_list.items))
        print(type(v1_namespace_list))
        return next(filter(lambda x: x.metadata.name == namespace_name,
                           v1_namespace_list.items), None)

    def create_namespace(self, namespace_name):
        v1ns = client.V1Namespace()
        v1ns.metadata = {'name': namespace_name}
        self.core_v1.create_namespace(body=v1ns)
        namespace_item = self.find_namespace(namespace_name)
        if namespace_item is None:
            raise ValueError('Failed to create namespace: ' + namespace_name)
        return namespace_item

    def find_or_create_namespace(self, target_namespace_name):
        namespace_item = self.find_namespace(target_namespace_name)

        if namespace_item is None:
            log('Namespace ' + target_namespace_name + 'does not exists. '
                'Creating.')
            namespace_item = self.create_namespace(target_namespace_name)

        log('Namespace info:\n' + str(namespace_item.metadata))

    def wait_for_all_resources(self, namespace_name):
        self.wait_for_all_pods_to_start(namespace_name)
        self.wait_for_all_replica_set(namespace_name)
        self.wait_for_all_deployments(namespace_name)

    def wait_for_all_pods_to_start(self, namespace_name):
        def format_containers(i):
            return '\n'.join(['\n        Containername: %s'
                              '\n                Ready: %s'
                              '\n              Waiting: %s' %
                              (c.name,
                               c.ready,
                               str(c.state.waiting).replace('\n', ''))
                              for c in i.status.container_statuses])
        log('Pods: Wait for all pods start')
        counter = 60
        while True:
            api_response = self.core_v1.list_namespaced_pod(namespace_name)
            #  log('\n'.join(['\nPodname: %s'
                           #  '\n    Phase: %s'
                           #  '\n    Containers: %s' %
                           #  (i.metadata.name, i.status.phase,
                            #  format_containers(i))
                           #  for i in api_response.items]))
            if all([i.status.phase == 'Running' and
                    all([cs.ready for cs in i.status.container_statuses])
                    for i in api_response.items]):
                break
            if counter > 0:
                counter = counter - 1
                log("Wait 10 sec for POD start up")
                time.sleep(10)
            else:
                pprint(api_response)
                raise ValueError('Timeout waiting for pods to reach '
                                 'Ready & Running')


    def wait_for_all_pods_to_terminate(self, namespace_name):
        log('Pods:')
        counter = 60
        while True:
            api_response = self.core_v1.list_namespaced_pod(namespace_name)
            if not api_response.items:
                break
            else:
                log('\n'.join(['\nPhase: %s  Podname: %s' %
                               (i.status.phase, i.metadata.name)
                               for i in api_response.items]))

            if counter > 0:
                counter = counter - 1
                time.sleep(10)
            else:
                raise ValueError('Timeout waiting for pods to terminate')

    def wait_for_all_deployments(self, namespace_name):
        api_response = self.apps_v1.list_namespaced_deployment(namespace_name)
        log('Deployments:')
        log([(i.metadata.name, 'Replicas ready/desired: (%s/%d)' %
              (str(i.status.ready_replicas), i.spec.replicas))
             for i in api_response.items])

    def wait_for_all_replica_set(self, namespace_name):
        api_response = self.apps_v1.list_namespaced_replica_set(namespace_name)
        log('Replica sets:')
        log([(i.metadata.name, 'Replicas ready/desired: (%s/%d)' %
              (str(i.status.ready_replicas), i.spec.replicas))
             for i in api_response.items])

    def wait_for_namespace_to_terminate(self, namespace_name):
        log('Namespace:')
        counter = 60
        while True:
            api_response = self.core_v1.list_namespace()
            flag = 0
            if not api_response.items:
                break
            else:
                for i in api_response.items:
                    if i.metadata.name == namespace_name:
                        flag = 1
                        break
                if flag == 1:
                    log('\n'.join(['\nPhase: %s  Namespace: %s' %
                                   (i.status.phase, i.metadata.name)
                                   for i in api_response.items]))
                else:
                    break

            if counter > 0:
                counter = counter - 1
                time.sleep(10)
            else:
                raise ValueError('Timeout waiting for namespace to terminate')


    def delete_namespace(self,namespace_name):
        log('Clean up residue in namespace '+namespace_name)
        namespace_item = self.find_namespace(namespace_name)
        if namespace_item is None:
            log('Namespace ' + namespace_name + ' does not exist.')
        else:
            log('Namespace info:\n' + str(namespace_item.metadata))
            body = client.V1DeleteOptions()
            api_response = self.core_v1.delete_namespace(namespace_name, body)
            log("Delete NAMESPACE: " + namespace_name)
            self.wait_for_namespace_to_terminate(namespace_name)

    def delete_all_pvcs(self,namespace_name):
         api_response = self.core_v1.delete_collection_namespaced_persistent_volume_claim(namespace_name)
         log('PVCs:')

    def delete_pod(self,pod_name,namespace_name):
        body = client.V1DeleteOptions()
        api_response = self.core_v1.delete_namespaced_pod(pod_name, namespace_name, body)
        time.sleep(2)
        log("Delete POD: " + pod_name)

    def scale_sts_pod(self,sts_name,namespace_name,replicas):
        log('Pods')
        counter = 60
        patch={"spec":{"replicas": replicas}}
        try:
            api_response = self.apps_v1.patch_namespaced_stateful_set_scale(sts_name,namespace_name, body=patch)
            time.sleep(2)
        except ApiException as e:
            print("Exception when calling AppsV1Api->patch_namespaced_stateful_set_scale: %s\n" % e)
            raise ValueError('Scale failed')

