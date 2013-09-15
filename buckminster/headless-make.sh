#! /bin/bash

rm -rf headless
./director/director \
	-r http://download.eclipse.org/tools/buckminster/headless-4.2/,http://download.spoofax.org/update/nightly/,http://download.eclipse.org/eclipse/updates/4.2 \
	-d headless \
	-p Buckminster \
	-i org.eclipse.buckminster.cmdline.product \
	-i org.eclipse.buckminster.core.headless.feature.feature.group \
	-i org.eclipse.buckminster.pde.headless.feature.feature.group \
	-i org.eclipse.buckminster.git.headless.feature.feature.group


#	-i org.eclipse.ui \
#	-i org.strategoxt.imp.feature.group
