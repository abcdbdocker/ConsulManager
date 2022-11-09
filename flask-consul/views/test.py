
# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/5/13 11:42
# @Author  : liuchengguo
# @File    : s.py
# @Description : 这个类封装kube-sdk


"""
自定义kube类
"""
import os
import sys

import kubernetes
import requests
from kubernetes import client, config



"""
kube类
"""
class Kube(object):

    def __init__(self, local=False, ten=False,ali=False):
        self.ten = None
        self.local = None
        self.ali = None

        if local:
            # self.config_file = "D:\pyrepair\Repair\Repair\libs\local-config"
            print("local yun")
            self.config_file = "local-config"
            self.local = "本地环境"
            config.kube_config.load_kube_config(config_file=self.config_file)

        elif ten:
            print("ten yun")
            # self.config_file = "D:\pyrepair\Repair\Repair\libs\\ten-config"
            self.config_file = "ten-config"
            self.ten = "腾讯云环境"
            config.kube_config.load_kube_config(config_file=self.config_file)

        elif os.name == "nt":
            self.config_file = "D:\pyrepair\Repair\Repair\libs\config"
            config.kube_config.load_kube_config(config_file=self.config_file)

        elif ali:
            print("ali yun")
            self.ali = "阿里云环境"
            self.config_file = "config"
            config.kube_config.load_kube_config(config_file=self.config_file)

        self.Api_Apps = client.AppsV1Api()
        self.Api_Instance = client.CoreV1Api()


    """获取空间"""
    def list_namespaces(self, namespace=None):
        namespaces = self.Api_Instance.list_namespace()

        for namespace_one in namespaces.items:
            if namespace_one.metadata.name == namespace:
                # print(namespace_one)

                workspace = namespace_one.metadata.labels.get("kubesphere.io/workspace")
                return  workspace


    """监听deployment对象"""
    def watch_all_namespaces_deployment(self):
        # watch = kubernetes.watch.Watch()
        # for e in watch.stream(self.Api_Instance.list_event_for_all_namespaces):
        #     print("操作:{0}\t\t空间:{1}\t\t服务:{2}".format(e.get("type"),e.get("object").metadata.namespace,e.get("object").metadata.name))
        deployment_list = self.Api_Apps.list_deployment_for_all_namespaces()
        len_deployment = len(deployment_list.items)
        new_len_add_deploy = []

        new_len_deployment = 1
        watch = kubernetes.watch.Watch()
        for e in watch.stream(self.Api_Apps.list_deployment_for_all_namespaces):
            if new_len_deployment <= len_deployment and e.get("type") == "ADDED":
                new_len_deployment += 1
            else:
                print("Start Listening")

                new_len_add_deploy.append(e.get("type"))
                namespace = e.get("object").metadata.namespace
                name = e.get("object").metadata.name
                kube_namespace = session.query(KubeModel).filter(KubeModel.kubenamespaces == namespace,
                                                                 KubeModel.status == 1).first()

                replicas = 0 if e.get("object").status.replicas == None else e.get("object").status.replicas
                ready_replicas = 0 if e.get("object").status.ready_replicas == None else e.get(
                    "object").status.ready_replicas

                workspace = self.list_namespaces(namespace=namespace)


                if self.local:
                    deploy = self.local
                    url =  "[{0}](https://k8s.lishicloud.com/{1}/clusters/intranet-dev/projects/{2}/deployments/{3}/resource-status)".format(
                        namespace,workspace,namespace,name)
                    # print(url)

                elif self.ten:
                    deploy = self.ten
                    url = "[{0}](https://k8s.lishicloud.com/{1}/clusters/tencent-prod/projects/{2}/deployments/{3}/resource-status)".format(
                        namespace, workspace, namespace, name)
                    # print(url)

                elif self.ali:
                    deploy = self.ali
                    url = "[{0}]https://k8s.lishicloud.com/{1}/clusters/intranet-dev/projects/{1}/deployments/{2}/resource-status".format(
                        workspace,namespace,name)
                else:
                    deploy = ""
                    url = ""

                try:
                    alias_name = e.get("object").metadata.annotations.get("kubesphere.io/alias-name") if e.get(
                        "object").metadata.annotations.get("kubesphere.io/alias-name") else "无别名"
                except Exception:
                    alias_name = "无别名"

                try:
                    description = e.get("object").metadata.annotations.get("kubesphere.io/description")if e.get(
                        "object").metadata.annotations.get("kubesphere.io/description") else "无描述"
                except Exception:
                    description = "无描述"


                try:
                    image = e.get("raw_object").get("spec").get("template").get("spec").get("containers")[0].get(
                        "image")
                except Exception:
                    print("非更新操作")
                    image = "无"

                "删除"
                if e.get("type") == "DELETED":

                    print("delete match", kube_namespace)
                    if kube_namespace:
                        msg_json = "**操作:** 删除告警 **环境:** {0} **空间:** {1} **服务:** {2} **服务别名:** {3} **服务描述:** {4} **当前镜像:** {5} **访问地址:** {6}".format(
                            deploy,namespace, name, alias_name, description, image,url)

                        self.send_msg(msg_json=msg_json, token=kube_namespace.token)
                        new_len_add_deploy = []
                    new_len_add_deploy = []

                "修改"
                if e.get("type") == "MODIFIED" and len(new_len_add_deploy) == 6:
                    print(new_len_add_deploy)

                    print("update match", kube_namespace)

                    if kube_namespace:
                        msg_json = "**操作:** 更新告警 **环境:** {0} **空间:** {1} **服务:** {2} **服务别名:** {3} **服务描述:** {4} **当前镜像:** {5}\n 访问地址: {6}".format(
                            deploy, namespace, name, alias_name, description, image, url)
                        self.send_msg(msg_json=msg_json, token=kube_namespace.token)
                        new_len_add_deploy = []
                    new_len_add_deploy = []

                "添加"
                if e.get("type") == "ADDED" and "ADDED" in new_len_add_deploy:
                    print("ADDED", new_len_add_deploy)

                    print("add match", kube_namespace)
                    if kube_namespace:
                        msg_json = "**操作:** 发布告警 **环境:** {0} **空间:** {1} **服务:** {2} **服务别名:** {3} **服务描述:** {4} **当前镜像:** {5} 访问地址: {6}".format(
                            deploy, namespace, name, alias_name, description, image, url)
                        self.send_msg(msg_json=msg_json, token=kube_namespace.token)
                        new_len_add_deploy = []
                    new_len_add_deploy = []

    """监听pod"""
    def watch_pod_deployment_namespace(self):
        watch = kubernetes.watch.Watch()
        pod_list = self.Api_Instance.list_pod_for_all_namespaces()
        len_pod = len(pod_list.items)
        new_len_add_pod = 1
        for e in watch.stream(self.Api_Instance.list_pod_for_all_namespaces):
            if new_len_add_pod <= len_pod and e.get("type") == "ADDED":
                new_len_add_pod += 1
            else:
                print("Start Listening Pod")

                print(e.get("object").status.phase)


    # 发送报警
    def send_msg(self, msg=None, token="331c2210aca410f0b3f333113579db3caacadca491a2e6060e2e3bbf2aafcf82",
                 msg_json=None):
        # print(msg_json)
        webhook_url = 'https://oapi.dingtalk.com/robot/send?access_token={0}'.format(token)
        headers = {'Content-Type': 'application/json;charset=utf-8'}

        if msg:
            msg_str = "## K8S-POD状态异常告警提示:\n\n  > **环境:** {0}\n\n  项目:{1}\t 服务名称:{2}\t当前状态:{3}\t 是否准备好:{4}\t 是否启动:{5}\t 重启次数:{6}\t".format(
                msg.get("deploy"),msg.get("project"), msg.get("service"), msg.get("status"), msg.get("reay"), msg.get("runing"),
                msg.get("restart"))
        else:
            msg_str = msg_json

        data = {
            "msgtype": "markdown",
            "markdown": {
                "title": "### K8S-POD状态异常告警提示:",
                "text": msg_str,
            },

            "at": {
                "atMobiles": 'reminders',
                "isAtAll": False,
            },
        }

        r = requests.post(url=webhook_url, json=data, headers=headers)
        #print(r.text)
        return r.text


if __name__ == '__main__':
    try:
        flag = sys.argv[1]
    except Exception:
        print("input local,ten,ali")
    print("transmission",flag)
    if flag == "local":
        client = Kube(local=True)
    elif flag == "ten":
        client = Kube(ten=True)
    elif flag == "ali":
        client = Kube(ali=True)
    # client = Kube(local=True)
    # client.watch_pod_deployment_namespace()
    client.watch_all_namespaces_deployment()
    # client = Kube()
    # client.send_msg()