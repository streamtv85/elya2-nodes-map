properties([pipelineTriggers([pollSCM('* * * * *')])])
node('master') {
	def version = VersionNumber(projectStartDate: '1970-01-01', versionNumberString: '.${BUILDS_ALL_TIME}', versionPrefix: "${env.RELEASE_NUMBER}", worstResultForIncrement: 'SUCCESS')
	withEnv(['REGISTRY=localhost:5000']) {
		stage('Build') {
			git url: 'https://github.com/streamtv85/elya2-nodes-map.git'
			echo "Registry address is ${env.REGISTRY}"
			echo "Building image version: ${version}"
			withDockerRegistry(url: "http://${env.REGISTRY}") {
				def customImage = docker.build("${env.REGISTRY}/jora/elya2map-app:${version}")
				customImage.push('latest')
			}
		}
	}
}

node('webapps') {
	withEnv(['REGISTRY=10.135.87.174:5000']) {
		stage('Test') {
			echo 'Reserved for Test stage'
		}
		stage('Deploy') {
			git url: 'https://github.com/streamtv85/elya2-nodes-map.git'
			echo "Registry address is ${env.REGISTRY}"
			echo 'Deploying application'
			sh 'bash ./deploy.sh'
		}
	}
}

