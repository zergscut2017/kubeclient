# kubeclient
My example code to access kubenetes-client and helm

KUBECONFIG='/home/zergscut/admin_config'
KUBECONFIG=${KUBECONFIG:-}

python3 test_stateful.py --kubernetes-admin-conf=${KUBECONFIG} --kubernetes-namespace=${NAMESAPCE} --chart-archive=${HELM_CHART_FILE} --helm-repo=${HELM_REPO} --baseline_chart_version=${BASELINE_CHART_VERSION} --kubernetes-namespace=deploytestcode-internal
