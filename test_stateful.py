#!/usr/bin/env python3

from KubernetesClient import KubernetesClient
from helm_agent import *
from utils import *
import unittest


class test_stateful:
    def __init__(self, args):
        self.target_namespace_name = args.kubernetes_namespace
        self.chart_archive = args.chart_archive
        self.chart_name = self.chart_archive.split('/')[1]
        self.helm_repo = args.helm_repo
        self.baseline_chart_version = args.baseline_chart_version
        self.kube = KubernetesClient(args.kubernetes_admin_conf)
        self.dependency_chart_archive = args.dependency_chart_archive

    def test_setup(self):
        log('Setup 1: Ensure that namespace exists ')
        self.kube.find_or_create_namespace(self.target_namespace_name)

        if self.dependency_chart_archive:
            log('Setup 2: Install dependency chart archive')
            helm_install_chart_archive('dependency-release',
                                       self.dependency_chart_archive,
                                       self.target_namespace_name)
            log('Setup 3: Wait for all resources to be up')
            self.kube.wait_for_all_resources(self.target_namespace_name)

            log('Setup 4: List releases')
            helm_list_releases(self.target_namespace_name)


    def test_teardown(self):
        if self.dependency_chart_archive:
            log('Teardown: Delete dependency release')
            helm_delete_release('dependency-release')
        log('Teardown: Clean up namespace')
        helm_cleanup_namespace(self.target_namespace_name)
        self.kube.wait_for_all_pods_to_terminate(self.target_namespace_name)
        self.kube.delete_namespace(self.target_namespace_name)


   
args = parse_args()
tc = test_stateful(args)
print(tc.target_namespace_name)
print(tc.kube)
print(tc.chart_name)
print(tc.helm_repo)
tc.test_setup()
tc.test_teardown()
