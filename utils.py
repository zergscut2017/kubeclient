#!/usr/bin/env python3
import argparse
import datetime
import os
import subprocess
import time

def parse_args():
    parser = argparse.ArgumentParser(
        description='Test tool for HELM installation and upgrade')
    parser.add_argument('-k', '--kubernetes-admin-conf',
                        dest='kubernetes_admin_conf',
                        type=str, required=True, metavar="KUBECONFIG",
                        help="Kubernetes admin conf to use")

    parser.add_argument('-n', '--kubernetes-namespace',
                        dest='kubernetes_namespace', type=str, required=True,
                        metavar='NAMESPACE',
                        help='Kubernetes namespace to use')

    parser.add_argument('-c', '--chart-archive',
                        dest='chart_archive', type=str, required=True,
                        metavar='CHART_ARCHIVE',
                        help='Helm chart archive to test')

    parser.add_argument('-d', '--dependency-chart-archive',
                        dest='dependency_chart_archive',
                        type=str, required=False,
                        metavar='DEPENDENCY_CHART_ARCHIVE',
                        help='Helm chart archive which contains the '
                             'implicit dependencies of the primary helm chart '
                             'which is under test')

    parser.add_argument('-r', '--helm-repo',
                        dest='helm_repo',
                        type=str, required=True, metavar='HELM_REPO',
                        help='Helm chart repository to get the baseline from')

    parser.add_argument('-b', '--baseline_chart_version',
                        dest='baseline_chart_version',
                        type=str, required=True, metavar='BASELINE_REVISION',
                        help='Revision of the baseline chart to upgrade from')

    args = parser.parse_args()
    if not args.kubernetes_admin_conf:
        raise ValueError('The environment variable KUBECONFIG is missing '
                         'or it is not passed as an argument to this program')
    if not os.path.isfile(args.kubernetes_admin_conf):
        raise ValueError('The value "' + args.kubernetes_admin_conf +
                         '" provided as the KUBECONFIG is not a readable file')

    if not args.chart_archive:
        raise ValueError('The --chart-archive argument is missing')

    if not os.path.isfile(args.chart_archive):
        raise ValueError('The value "' + args.chart_archive + '" provided as'
                         ' the CHART_ARCHIVE is not a readable file')

    if args.dependency_chart_archive and not os.path.isfile(
            args.dependency_chart_archive):
        raise ValueError('The value "' + args.dependency_chart_archive +
                         '" provided as the DEPENDENCY_CHART_ARCHIVE is '
                         'not a readable file')

    return args

def d(t0):
    return str(datetime.datetime.now() - t0)


def log(*message):
    now = datetime.datetime.now()
    print(now.date().isoformat() + ' ' + now.time().isoformat() +
          ': ' + str(*message))

def execute_command(command):
    log('Executing: ' + '"' + command + '"')
    process = subprocess.Popen(command.split(' '), stdout=subprocess.PIPE)
    process.wait()
    output = process.stdout.read().decode('utf-8')
    print(output)
    if process.returncode != 0:
        raise ValueError('Command return unexpected error code: %d' %
                         process.returncode)
    return output


