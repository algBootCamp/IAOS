# app运行脚本
source ../iaosenv/bin/activate
export FLASK_APP=../app/app
#export FLASK_ENV=production

# flask run --help
#flask run --reload --debugger -p 8888
# reload：热加载  debugger：debug模式
flask run -p 8888
#flask start-iaos dev
