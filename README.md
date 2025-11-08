##  Atencion! Estamos trabajando👋
<p float="center">
  <img  src="https://github-readme-stats.vercel.app/api/top-langs/?username=cossioyee&layout=compact&hide=html,css" alt="Top Languages" />
</p>




## Languages and Tools:
<p align="left">
    <a href="https://aws.amazon.com" target="_blank" rel="noreferrer">
        <img style="border: 1px solid #ddd; border-radius: 4px; padding: 5px;" src="https://raw.githubusercontent.com/devicons/devicon/master/icons/amazonwebservices/amazonwebservices-original-wordmark.svg" alt="aws" width="40" height="40"/>
    </a>
    <a href="https://www.docker.com/" target="_blank" rel="noreferrer">
        <img style="border: 1px solid #ddd; border-radius: 4px; padding: 5px;" src="https://raw.githubusercontent.com/devicons/devicon/master/icons/docker/docker-original-wordmark.svg" alt="docker" width="40" height="40"/>
    </a>
    <a href="https://git-scm.com/" target="_blank" rel="noreferrer">
        <img style="border: 1px solid #ddd; border-radius: 4px; padding: 5px;" src="https://www.vectorlogo.zone/logos/git-scm/git-scm-icon.svg" alt="git" width="40" height="40"/>
    </a>
    <a href="https://www.jenkins.io" target="_blank" rel="noreferrer">
        <img style="border: 1px solid #ddd; border-radius: 4px; padding: 5px;" src="https://www.vectorlogo.zone/logos/jenkins/jenkins-icon.svg" alt="jenkins" width="40" height="40"/>
    </a>
    <a href="https://kubernetes.io" target="_blank" rel="noreferrer">
        <img style="border: 1px solid #ddd; border-radius: 4px; padding: 5px;" src="https://www.vectorlogo.zone/logos/kubernetes/kubernetes-icon.svg" alt="kubernetes" width="40" height="40"/>
    </a>
</p>

## Connect with me

<div align="center"><a href="www.linkedin.com/in/jeancossio" target="_blank">
<img src=https://img.shields.io/badge/linkedin-%231E77B5.svg?&style=for-the-badge&logo=linkedin&logoColor=white alt=linkedin style="margin-bottom: 5px;" />
</a>
<a href="https://github.com/cossioyee" target="_blank">
<img src=https://img.shields.io/badge/github-%2324292e.svg?&style=for-the-badge&logo=github&logoColor=white alt=github style="margin-bottom: 5px;" />
</a>

<a href="https://www.instagram.com/jcossio16" target="_blank">
<img src=https://img.shields.io/badge/instagram-%23000000.svg?&style=for-the-badge&logo=instagram&logoColor=white alt=instagram style="margin-bottom: 5px;" />
</a>

</div>
<!--
**cossioyee/cossioyee** is a ✨ _special_ ✨ repository because its `README.md` (this file) appears on your GitHub profile.

Here are some ideas to get you started:

- 🔭 I’m currently working on ...
- 🌱 I’m currently learning ...
- 👯 I’m looking to collaborate on ...
- 🤔 I’m looking for help with ...
- 💬 Ask me about ...
- 📫 How to reach me: ...
- 😄 Pronouns: ...
- ⚡ Fun fact: ...
-->

Your Kubernetes control-plane has initialized successfully!

To start using your cluster, you need to run the following as a regular user:

  mkdir -p $HOME/.kube
  sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
  sudo chown $(id -u):$(id -g) $HOME/.kube/config

Alternatively, if you are the root user, you can run:

  export KUBECONFIG=/etc/kubernetes/admin.conf

You should now deploy a pod network to the cluster.
Run "kubectl apply -f [podnetwork].yaml" with one of the options listed at:
  https://kubernetes.io/docs/concepts/cluster-administration/addons/
94489089218c9e20ae8733c9eda39970f203c8b632d238e0fc332ea33388c081
Then you can join any number of worker nodes by running the following on each as root:

kubeadm join 192.168.0.100:6443 --token clj0z5.oup1gfiy0lb1lmmr \
        --discovery-token-ca-cert-hash sha256:c7a6829278b211a780e03eb0cda1295fb6765887e8d445008a76eb2bb8353a6b

mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/

sudo kubeadm reset -f
sudo rm -rf /etc/kubernetes/manifests/*
sudo rm -rf /var/lib/etcd/*
sudo systemctl restart kubelet

kubeadm init --pod-network-cidr=10.244.0.0/

kubectl apply -f https://raw.githubusercontent.com/coreos/flannel/master/Documentation/kube-flannel.yml --validate=false

kubectl apply -f https://raw.githubusercontent.com/coreos/flannel/master/Documentation/kube-flannel.yml

kubeadm join 192.168.0.100:6443 --token mlssms.c9j564rvqt6vb4mb \
        --discovery-token-ca-cert-hash sha256:



kubectl drain worker1 --delete-local-data --force --ignore-daemonsets
kubectl delete node worker1

sudo kubeadm reset
sudo rm -rf /etc/cni /var/lib/cni /var/lib/kubelet /etc/kubernetes /var/lib/etcd
sudo ip link delete cni0
sudo ip link delete flannel.1  # Si estás usando Flannel
sudo iptables -F && sudo iptables -t nat -F && sudo iptables -t mangle -F && sudo iptables -X



cat <<EOF | sudo tee /etc/modules-load.d/k8s.conf
overlay
br_netfilter
EOF

cat <<EOF | sudo tee /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-iptables  = 1
net.ipv4.ip_forward                 = 1
net.bridge.bridge-nf-call-ip6tables = 1
EOF

sudo modprobe br_netfilter
sudo sysctl --system
