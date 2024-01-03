#install terraform in aws cli console
#run "chmod u+x install_terraform.sh" before executing this file


sudo yum install -y yum-utils shadow-utils
sudo yum-config-manager --add-repo https://rpm.releases.hashicorp.com/AmazonLinux/hashicorp.repo
sudo yum -y install terraform

