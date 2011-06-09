# Source this file to gain access to the t3 tools


previous_PWD=$PWD
previous_OLDPWD=$OLDPWD
cd $(dirname $BASH_SOURCE)
export T3T_SETUP_DIR="$(pwd -P)"
cd $previous_PWD
OLDPWD=$previous_OLDPWD

unset previous_PWD
unset previous_OLDPWD

export PATH=$T3T_SETUP_DIR:$PATH

complete -o nospace -C $T3T_SETUP_DIR/t3tools.py t3ls
complete -o nospace -C $T3T_SETUP_DIR/t3tools.py t3get
complete -o nospace -C $T3T_SETUP_DIR/t3tools.py t3mkdir
complete -o nospace -C $T3T_SETUP_DIR/t3tools.py t3mv 
complete -o nospace -C $T3T_SETUP_DIR/t3tools.py t3put
complete -o nospace -C $T3T_SETUP_DIR/t3tools.py t3rm