#set -e
export PATH=$PATH:~/arc32/bin:~/kw/kw10.3.0/bin
url='http://findlay-ubuntu.amr.corp.intel.com:8080'
proj="corelibs-atlasedge-master"
#make -f Makefile.corelibs clean
kwinject make -f Makefile.corelibs
kwbuildproject --url $url/$proj -f -o ~/kw/kwtables kwinject.out
kwadmin --url $url load $proj ~/kw/kwtables/
