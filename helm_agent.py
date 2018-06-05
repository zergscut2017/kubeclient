#!/usr/bin/env python3

from utils import *

def helm_list_releases(namespace_name):
    list_command = 'helm ls --all --namespace=' + namespace_name
    execute_command(list_command)

def helm_cleanup_namespace(namespace_name):
    log('Cleaning up namespace delete all releases in namespace')
    name = execute_command('helm ls --all --namespace=' + namespace_name +
                           ' -q')
    name = name.replace('\n', ' ').strip()
    if name:
        helm_delete_release(name)
    else:
        log('There is no release in namespace ' + namespace_name)




def helm_delete_release(release_name):
    log('Deleting release(s)')
    delete_command = ('helm delete --debug --purge --timeout=20000 ' +
                      release_name)
    execute_command(delete_command)


def helm_install_chart_archive(name, chart_archive, namespace_name):
    install_command = ('helm install --debug --name=' + name + ' ' +
                       chart_archive +
                       ' --namespace=' + namespace_name +
                       ' --wait --timeout 20000')
    return execute_command(install_command)

def helm_install_chart_no_debug(name, chart_archive, namespace_name):
    install_command = ('helm install --name=' + name + ' ' +
                       chart_archive +
                       ' --namespace=' + namespace_name +
                       ' --wait --timeout 20000')
    return execute_command(install_command)

def helm_chart_test(release_name):
    log('chart test for '+ release_name)
    test_command = ('helm test ' + release_name + " --debug --cleanup")
    execute_command(test_command)

def helm_install_chart_from_repo(helm_repo, chart_name, chart_version,
                                 release_name, target_namespace_name):
    log('Adding helm repo')
    repo_add_command = ('helm repo add --home=/home/helmuser/.helm'
                        ' --debug ' + 'BASELINE' + ' ' + helm_repo)
    execute_command(repo_add_command)

    log('Installing chart')
    baseline_install_command = ('helm install --home=/home/helmuser/.helm '
                                '--debug --namespace=' +
                                target_namespace_name +
                                ' BASELINE/' + chart_name + ' '
                                '--version=' + chart_version +
                                ' --wait --timeout 20000' +
                                ' --name=' + release_name)
    execute_command(baseline_install_command)


def helm_wait_for_deployed_release_to_appear(expected_release_name,
                                             target_namespace_name):

    log('Waiting for helm release to reach deployed state')
    counter = 10
    while True:
        release_name = execute_command('helm ls --deployed ' +
                                       expected_release_name +
                                       ' --namespace=' +
                                       target_namespace_name + ' -q').rstrip()

        if release_name == expected_release_name:
            return
        log('%s != %s' % (str(release_name), expected_release_name))
        if counter > 0:
            counter = counter - 1
            time.sleep(3)
        else:
            raise ValueError('Timeout waiting for release to reach '
                             ' deployed state')


def helm_upgrade_with_chart_archive(baseline_release_name, chart_archive,
                                    target_namespace_name):
    release_name = execute_command('helm ls --deployed ' +
                                   baseline_release_name +
                                   ' --namespace=' +
                                   target_namespace_name + ' -q').rstrip()

    if not release_name or release_name != baseline_release_name:
        raise ValueError('Unable to find expected baseline release: ' +
                         baseline_release_name)

    upgrade_command = ('helm upgrade %s %s --namespace %s --debug --wait '
                       '--timeout 20000' % (baseline_release_name,
                                            chart_archive,
                                            target_namespace_name))
    execute_command(upgrade_command)



