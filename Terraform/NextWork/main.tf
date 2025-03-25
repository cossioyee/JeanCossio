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
      "source ~/.bashrc",
      "mvn -v",
      "java -version",
      "mvn archetype:generate -DgroupId=com.nextwork.app -DartifactId=nextwork-web-project -DarchetypeArtifactId=maven-archetype-webapp -DinteractiveMode=false",
      "sudo dnf update -y",
      "sudo dnf install -y git",
      "git --version"
    ]

    connection {
      type        = "ssh"
      user        = "ec2-user" // Replace with the appropriate username for your AMI
      private_key = file("~/.ssh/myWebAppKeyPair.pem") // Path to your private key
      host        = self.public_ip
    }
  }
}
