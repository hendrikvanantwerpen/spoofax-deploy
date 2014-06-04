#! /bin/bash

rm -rf headless
./director/director \
	-r http://download.eclipse.org/tools/buckminster/headless-4.3/,http://download.eclipse.org/eclipse/updates/4.3 \
	-d headless \
	-p Buckminster \
	-i org.eclipse.buckminster.cmdline.product \
	-i org.eclipse.buckminster.core.headless.feature.feature.group \
	-i org.eclipse.buckminster.pde.headless.feature.feature.group \
	-i org.eclipse.buckminster.git.headless.feature.feature.group


#	-i org.eclipse.ui \
#	-i org.strategoxt.imp.feature.group
