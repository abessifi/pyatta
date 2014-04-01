#!../bin/python
import os
import ConfigParser

class sessionconfig():

    def set_config_params(self,tag,key):
        config = ConfigParser.SafeConfigParser()
        config.readfp(open('/home/vyos/vyos-api/VyosApi.conf'))
        return config.get(tag,key)

    def setup_config_session(self,shell_api_path):
        return ("""
                session_env=$(%s getSessionEnv $PPID)
                eval $session_env
                %s setupSession

                %s inSession
                if [ $? -ne 0 ]; then
                    echo "Something went wrong!"
                fi
                """ % (shell_api_path,shell_api_path,shell_api_path))


