@Library('powerpony') _

pipeline {
    agent any
    environment {
        PYPI_USERNAME   = credentials('pypi_username')
        PYPI_PASS       = credentials('pypi_pass')
    }
    stages {
        stage("Clone repo") {
          steps {
                git(
                  credentialsId: "s-radex_ssh",
                  branch: "${GIT_BRANCH}",
                  url: "${GIT_REPOSITORY_LINK}")

          }
        }
        stage("Push ds-netcraft to PyPI repository") {
            agent {
                docker {
                    image 'python'
                    args '-e ${PYPI_USERNAME}=${PYPI_USERNAME}'
                }
            }
            when {
                not {
                    branch 'master'
                }
            }
            steps {
                sh '''
                   # just in case if the last command will not execute
                   rm -rf env
                   python3 -m venv env
                   . env/bin/activate
                   pip install twine wheel
                   rm -rf dist
                   python setup.py bdist_wheel
                   twine upload  --repository-url ${PYPI_URL} -u ${PYPI_USERNAME} -p ${PYPI_PASS} dist/* --verbose
                   deactivate
                   cd ${WORKSPACE}
                   rm -rf env
                '''
            }
        }
    }
}
