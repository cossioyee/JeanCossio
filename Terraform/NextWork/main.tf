terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16"
    }
  }

  required_version = ">= 1.2.0"
}

provider "aws" {
  region  = "us-east-1"
}

resource "aws_instance" "app_server" {
  ami           = "ami-08b5b3a93ed654d19"
  instance_type = "t2.micro"
  vpc_security_group_ids = [
    "sg-0982f4b699100a2b5"
  ]
  key_name = "myWebAppKeyPair"
  iam_instance_profile = "EC2-instance-nextwork-cicd"
  tags = {
    Name = "NextWork-WebApp"
  }

  provisioner "remote-exec" {
    inline = [
      "wget https://archive.apache.org/dist/maven/maven-3/3.5.2/binaries/apache-maven-3.5.2-bin.tar.gz",
      "sudo tar -xzf apache-maven-3.5.2-bin.tar.gz -C /opt",
      "sudo dnf install -y java-1.8.0-amazon-corretto-devel",
      "echo 'export JAVA_HOME=/usr/lib/jvm/java-1.8.0-amazon-corretto.x86_64' >> ~/.bashrc",
      "echo 'export PATH=/usr/lib/jvm/java-1.8.0-amazon-corretto.x86_64/jre/bin/:/opt/apache-maven-3.5.2/bin:$PATH' >> ~/.bashrc",
      "echo 'export CODEARTIFACT_AUTH_TOKEN=`aws codeartifact get-authorization-token --domain nextwork --domain-owner 742925356489 --region us-east-1 --query authorizationToken --output text`' >> ~/.bashrc",
      "source ~/.bashrc",
      "mvn -v",
      "java -version",
      "mkdir nextwork-web-project",
      "sudo dnf update -y",
      "sudo dnf install -y git",
      "git --version",
      "cd nextwork-web-project",
      "git init",
      "git remote add origin https://github.com/cossioyee/nextwork-web-project.git",
      "git pull origin master",
      "mvn -s settings.xml compile"
    ]

    connection {
      type        = "ssh"
      user        = "ec2-user" // Replace with the appropriate username for your AMI
      private_key = file("~/.ssh/myWebAppKeyPair.pem") // Path to your private key
      host        = self.public_ip
    }
  }
}