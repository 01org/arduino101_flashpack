set -e
export PATH=$PATH:~/arc32/bin:~/kw/kw10.3.0/bin
url='http://findlay-ubuntu.amr.corp.intel.com:8080'
proj="corelibs-atlasedge-master"
if [ -n "$1" ]; then
  proj="$1"
fi
if [ -n "$KW_BUILD" ]; then
  build="--name $KW_BUILD"
fi
#make -f Makefile.corelibs clean
kwinject make -f Makefile.corelibs
kwbuildproject --url $url/$proj -f -o ~/kw/kwtables kwinject.out
kwadmin --url $url load $build $proj ~/kw/kwtables/
