// vim: ft=groovy
@Library('Jenkins-Shared-Libraries') _

pipeline {
  agent { 
    node {
      label 'docker'
    }
  }
  // parameters {
  // 	string(name: 'SOURCE_IMAGE_TAG', defaultValue: '', description: 'Setter for new Image Version.')
  // }
  options {
    buildDiscarder logRotator(
        artifactDaysToKeepStr: '', 
        artifactNumToKeepStr: '', 
        daysToKeepStr: '30', 
        numToKeepStr: '10')
      timeout(time: 90, unit: 'MINUTES')
      disableResume()
      gitLabConnection('code.dev.sbb.berlin')
      gitlabBuilds(builds: ['build', 'deploy-docker'])
      // sendSplunkConsoleLog()
  }

  stages{

    stage('Set up variables') {
      steps {
        script {
          echo 'Use release nexus'
            env.DOCKER_REPO_ID = "artefakt.dev.sbb.berlin:5005"
            echo 'Determine OCR-D version'
            env.OCRD_VERSION = readFile 'VERSION'
            echo 'Set Docker tag'
            env.OCRD_DOCKER_TAG = 'sbb/ocrd_core'
        }
      }
    }

    stage('Build Docker image'){
      steps {
        catchError(stageResult: 'FAILURE', buildResult: currentBuild.result) {
          gitlabCommitStatus("build_docker"){
            sh "make docker DOCKER_BASE_IMAGE='artefakt.dev.sbb.berlin:5000/sbb/base-images/debian12' DOCKER_TAG=$OCRD_DOCKER_TAG"
          }
        }
      }
    }

    stage('Deploy Docker image') {
      steps {
        catchError(stageResult: 'FAILURE', buildResult: currentBuild.result) {
          gitlabCommitStatus("deploy-docker"){
            withCredentials([[
                $class: 'UsernamePasswordMultiBinding',
                credentialsId: 'nexus-docker-deploy',
                usernameVariable: 'USR',
                passwordVariable: 'PWD'
            ]]) {
              sh "docker login -u $USR -p $PWD $DOCKER_REPO_ID"
            }
            script {
              env.OCRD_DOCKER_TAG_VERSIONED = env.DOCKER_REPO_ID + '/' + env.OCRD_DOCKER_TAG + ':' + env.OCRD_VERSION
            }
            sh "docker tag $OCRD_DOCKER_TAG $OCRD_DOCKER_TAG_VERSIONED"
            sh "docker push $OCRD_DOCKER_TAG_VERSIONED"
            sh "docker logout $DOCKER_REPO_ID"
            sh "docker image rm -f $OCRD_DOCKER_TAG $OCRD_DOCKER_TAG_VERSIONED"
          }
        }
      }
    }

    stage('Git Tag'){
      when {
        beforeOptions true
          environment name: 'BUILD_TYPE', value: 'release'
      }
      steps{
        catchError(stageResult: 'FAILURE', buildResult: currentBuild.result) {
          gitlabCommitStatus("git-tag"){
            git_tag_release()
          }
        }
      }
    }
  }
  post {
    always {
      // Run the steps in the post section regardless of the completion status of the Pipeline’s or stage’s run.
      echo 'This will always run'
    }
    unstable {
      // Only run the steps in post if the current Pipeline’s or stage’s run has an "unstable" status, usually caused by test failures, code violations, etc. This is                            typically denoted by yellow in the web UI.
      echo 'Build is unstable'
        status_mail()
    }
    notBuilt {
      // One or more steps need to be included within each condition's block.
      echo 'Runs as last Post condition'
    }
    regression {
      // Only run the steps in post if the current Pipeline’s or stage’s run’s status is failure, unstable, or aborted and the previous run was successful.
      echo 'Build has changed to unsuccessful'
    }
    aborted {
      // Only run the steps in post if the current Pipeline’s or stage’s run has an "aborted" status, usually due to the Pipeline being manually aborted. This is typically                      denoted by gray in the web UI.
      echo 'Build was aborted'
        status_mail()
        updateGitlabCommitStatus name: 'build', state: 'canceled'
    }
    success {
      // Only run the steps in post if the current Pipeline’s or stage’s run has a "success" status, typically denoted by blue or green in the web UI.
      echo 'Build is successful'
        script{
          if(env.EMAIL_SENDALWAYS)
            status_mail()
              if(env.GIT_BRANCH.contains('public'))
                updateGitlabCommitStatus name: 'deploy-docker', state: 'success'
        }
    }
    failure {
      // Only run the steps in post if the current Pipeline’s or stage’s run has a "failed" status, typically denoted by red in the web UI.
      echo 'Build is failed'
        status_mail()
        updateGitlabCommitStatus name: 'build', state: 'failed'
    }
    unsuccessful {
      // Only run the steps in post if the current Pipeline’s or stage’s run has not a "success" status. This is typically denoted in the web UI depending on the status                         previously mentioned
      echo 'Build has no success status'
    }
    fixed {
      // Only run the steps in post if the current Pipeline’s or stage’s run is successful and the previous run failed or was unstable.
      echo 'Build is now fixed'
    }
    changed {
      // Only run the steps in post if the current Pipeline’s or stage’s run has a different completion status from its previous run.
      echo 'Build status of the Pipeline has changed'
    }
    cleanup {
      // Run the steps in this post condition after every other post condition has been evaluated, regardless of the Pipeline or stage’s status.
      deleteDir() /* clean up build dir */
        cleanWs() /* clean up workspace */
        dir("${env.WORKSPACE_TMP}") {
          deleteDir()
        }
      sh "docker system prune --all --force --filter=until=240h"
        echo 'Build is cleaned'
        script {
          env.STATUS = currentBuild.result
            env.TRIGGER = env.GIT_BRANCH.contains('master') || env.GIT_BRANCH.contains('main') ? 'true'.toBoolean() : 'false'.toBoolean()
        }
    }
  }
}

