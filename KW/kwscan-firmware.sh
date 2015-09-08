#set -e
export PATH=$PATH:~/kw/kw10.3.0/bin
url='http://findlay-ubuntu.amr.corp.intel.com:8080'
proj="firmware"
make -C thunderdome/projects/atlaspeak_atlasedge setup
kwinject make -C thunderdome/projects/atlaspeak_atlasedge image
kwbuildproject --url $url/$proj -f -o ~/kw/kwtables \
   --add-compiler-options "-I ${PWD}/thunderdome/external/gcc-arc-elf32/arc-elf32/include" \
   kwinject.out
kwadmin --url $url load $proj ~/kw/kwtables/
