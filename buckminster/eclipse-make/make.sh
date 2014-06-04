#! /bin/bash

# Exit on interruption.
function terminate() { exit $?; }
trap terminate SIGINT


# Selection Eclipse and Spoofax repositories.
PWD=`pwd`;

if [ -d "$PWD/mirror-eclipse/" ]; then
  ECLIPSE_REPO="file://$PWD/mirror-eclipse/";
  echo "Using mirrored Eclipse repository: $ECLIPSE_REPO";
else
  ECLIPSE_REPO="http://download.eclipse.org/eclipse/updates/4.3";
  echo "Using online Eclipse repository: $ECLIPSE_REPO";
fi

if [ -d "$PWD/mirror-egit/" ]; then
  EGIT_REPO="file://$PWD/mirror-egit/";
  echo "Using mirrored EGit repository: $EGIT_REPO";
else
  EGIT_REPO="http://download.eclipse.org/egit/updates";
  echo "Using online Eclipse repository: $EGIT_REPO";
fi

if [ -d "$PWD/mirror-spoofax/" ]; then
  SPOOFAX_REPO="file://$PWD/mirror-spoofax/";
  echo "Using mirrored Spoofax repository: $SPOOFAX_REPO";
else
  SPOOFAX_REPO="http://download.spoofax.org/update/unstable/";
  echo "Using online Spoofax repository: $SPOOFAX_REPO";
fi


# Function to generate an Eclipse installation.
function eclipse {

  # 1. os
  # 2. ws
  # 3. arch
  # 4. ini path
  # 5. JRE path relative to ini file

  echo "Creating Eclipse installation for $1 $2 $3";

  INSTALL_PATH="spoofax-$1-$3";
  INSTALL_NOJAVA_ZIP="spoofax-$1-$3-nojre.zip";
  INSTALL_ZIP="spoofax-$1-$3.zip";
  INI_PATH="$INSTALL_PATH/$4";

  # Delete old stuff
  rm -rf $INSTALL_PATH;
  rm -rf $INSTALL_NOJAVA_ZIP;
  rm -rf $INSTALL_ZIP;

  # Create eclipse installation
  ../director/director \
    -repository $ECLIPSE_REPO,$SPOOFAX_REPO,$EGIT_REPO \
    -destination $INSTALL_PATH \
    -bundlepool $INSTALL_PATH \
    -profile SDKProfile \
    -profileProperties org.eclipse.update.install.features=true \
    -installIU org.eclipse.sdk.ide \
    -installIU org.eclipse.jdt.feature.group \
    -installIU org.eclipse.jdt.source.feature.group \
    -installIU org.eclipse.pde.feature.group \
    -installIU org.eclipse.pde.source.feature.group \
    -installIU org.eclipse.jgit.feature.group \
    -installIU org.eclipse.egit.feature.group \
    -installIU org.strategoxt.imp.feature.group \
    -p2.os $1 \
    -p2.ws $2 \
    -p2.arch $3 \
    -roaming;

  # Remove regular VM args
  sed -i '' -e 's|-Xms[0-9]*m||' $INI_PATH;
  sed -i '' -e 's|-Xss[0-9]*m||' $INI_PATH;
  sed -i '' -e 's|-Xmx[0-9]*m||' $INI_PATH;
  sed -i '' -e 's|-XX:MaxPermSize=[0-9]*m||' $INI_PATH;
  perl -pi -0 -w -e "s/-install\n.+//g" $INI_PATH;
  sed -i '' -e '/^$/d' $INI_PATH;
  perl -pi -e "s/^\r\n//" $INI_PATH;

  # Add own VM arguments
  echo "-Xms512m" >> $INI_PATH;
  echo "-Xmx1024m" >> $INI_PATH;
  echo "-Xss16m" >> $INI_PATH;
  echo "-XX:MaxPermSize=256m" >> $INI_PATH;
  echo "-server" >> $INI_PATH;

  # Create an archive without JRE
  echo "Archiving without JRE included: $INSTALL_NOJAVA_ZIP";
  zip -q -r $INSTALL_NOJAVA_ZIP $INSTALL_PATH;


  # Create an archive with JRE
  JRE_PATH="jre/$1_$3";
  if [ -d "$JRE_PATH" ]; then
    echo "Including JRE from $JRE_PATH";

    JRE_TARGET_PATH="$INSTALL_PATH/jre";
    JRE_RELATIVE_TO_INI_PATH="$5";
    
    # Copy JRE into Eclipse directory
    mkdir -p $JRE_TARGET_PATH;
    cp -R "$JRE_PATH/." $JRE_TARGET_PATH;

    # Prepend VM argument
    sed -i '' -e "1s;^;-vm@$JRE_RELATIVE_TO_INI_PATH@;" $INI_PATH;
    tr "@" "\n" < $INI_PATH > "$INI_PATH.tmp";
    rm $INI_PATH;
    mv "$INI_PATH.tmp" $INI_PATH;

    # Zip it with JRE
    echo "Archiving with JRE included: $INSTALL_ZIP";
    zip -q -r $INSTALL_ZIP $INSTALL_PATH;
  else
    echo "No JRE found for $1 $3";
  fi


  # Delete installation folder
  rm -rf $INSTALL_PATH;

}


# Create Eclipse installations for supported platforms.
eclipse "macosx" "cocoa" "x86_64" "Eclipse.app/Contents/MacOS/eclipse.ini" "../../../jre/bin/java";
eclipse "macosx" "cocoa" "x86" "Eclipse.app/Contents/MacOS/eclipse.ini" "../../../jre/bin/java";
eclipse "win32" "win32" "x86_64" "eclipse.ini" "jre\\\bin\\\javaw.exe";
eclipse "win32" "win32" "x86" "eclipse.ini" "jre\\\bin\\\javaw.exe";
eclipse "linux" "gtk" "x86_64" "eclipse.ini" "jre/bin/java";
eclipse "linux" "gtk" "x86" "eclipse.ini" "jre/bin/java";
