from collections import OrderedDict
from os import path
import shutil

from metaborg.util.git import LatestDate
from metaborg.util.maven import Mvn, MvnSetingsGen, MvnUserSettingsLocation


def BuildAll(repo, components = ['all'], buildDeps = True, resumeFrom = None, buildStratego = False,
    bootstrapStratego = False, strategoTest = True, cleanRepo = True, release = False, deploy = False, clean = True,
    profiles = [], **mavenArgs):
  basedir = repo.working_tree_dir
  if release:
    profiles.append('release')
    buildStratego = True
    bootstrapStratego = True
    strategoTest = True
    clean = True
  if bootstrapStratego:
    buildStratego = True

  if cleanRepo:
    CleanLocalRepo()

  profiles.append('!add-metaborg-repositories')

  qualifier = CreateQualifier(repo)
  print('Using Eclipse qualifier {}.'.format(qualifier))

  if buildDeps:
    buildOrder = GetBuildOrder(components)
  else:
    buildOrder = components

  print('Building component(s): {}'.format(', '.join(buildOrder)))
  for build in buildOrder:
    print('Building: {}'.format(build))
    cmd = GetBuildCommand(build)
    cmd(basedir = basedir, deploy = deploy, qualifier = qualifier, noSnapshotUpdates = True, clean = clean,
        profiles = profiles, buildStratego = buildStratego, bootstrapStratego = bootstrapStratego,
        strategoTest = strategoTest, resumeFrom = resumeFrom, **mavenArgs)


def BuildPoms(basedir, deploy, qualifier, buildStratego, bootstrapStratego, strategoTest, **kwargs):
  phase = 'deploy' if deploy else 'install'
  pomFile = path.join(basedir, 'spoofax-deploy', 'org.metaborg.maven.build.parentpoms', 'pom.xml')
  Mvn(pomFile = pomFile, phase = phase, **kwargs)


def BuildOrDownloadStrategoXt(basedir, deploy, buildStratego, bootstrapStratego, strategoTest, **kwargs):
  if buildStratego:
    BuildStrategoXt(basedir = basedir, deploy = deploy, bootstrap = bootstrapStratego, runTests = strategoTest, **kwargs)
  else:
    DownloadStrategoXt(basedir, **kwargs)

def DownloadStrategoXt(basedir, clean, profiles, **kwargs):
  if '!add-metaborg-repositories' in profiles:
    profiles.remove('!add-metaborg-repositories')
  pomFile = path.join(basedir, 'strategoxt', 'strategoxt', 'download-pom.xml')
  Mvn(pomFile = pomFile, clean = False, profiles = profiles, phase = 'dependency:resolve', **kwargs)

def BuildStrategoXt(basedir, profiles, deploy, bootstrap, runTests, **kwargs):
  if '!add-metaborg-repositories' in profiles:
    profiles.remove('!add-metaborg-repositories')

  strategoXtDir = path.join(basedir, 'strategoxt', 'strategoxt')
  phase = 'deploy' if deploy else 'install'

  if bootstrap:
    pomFile = path.join(strategoXtDir, 'bootstrap-pom.xml')
  else:
    pomFile = path.join(strategoXtDir, 'build-pom.xml')
  buildKwargs = dict(kwargs)
  buildKwargs.update({'strategoxt-skip-test': not runTests})
  Mvn(pomFile = pomFile, phase = phase, profiles = profiles, **buildKwargs)

  parent_pom_file = path.join(strategoXtDir, 'buildpoms', 'pom.xml')
  buildKwargs = dict(kwargs)
  buildKwargs.update({'strategoxt-skip-build': True, 'strategoxt-skip-assembly' : True})
  Mvn(pomFile = parent_pom_file, phase = phase, profiles = profiles, **buildKwargs)


def BuildJava(basedir, qualifier, deploy, buildStratego, bootstrapStratego, strategoTest, **kwargs):
  phase = 'deploy' if deploy else 'install'
  pomFile = path.join(basedir, 'spoofax-deploy', 'org.metaborg.maven.build.java', 'pom.xml')
  Mvn(pomFile = pomFile, phase = phase, forceContextQualifier = qualifier, **kwargs)

def BuildEclipse(basedir, qualifier, deploy, buildStratego, bootstrapStratego, strategoTest, **kwargs):
  phase = 'deploy' if deploy else 'install'
  pomFile = path.join(basedir, 'spoofax-deploy', 'org.metaborg.maven.build.spoofax.eclipse', 'pom.xml')
  Mvn(pomFile = pomFile, phase = phase, forceContextQualifier = qualifier, **kwargs)

def BuildPluginPoms(basedir, deploy, qualifier, buildStratego, bootstrapStratego, strategoTest, **kwargs):
  phase = 'deploy' if deploy else 'install'
  pomFile = path.join(basedir, 'spoofax-deploy', 'org.metaborg.maven.build.parentpoms.plugin', 'pom.xml')
  kwargs.update({'skip-language-build' : True})
  Mvn(pomFile = pomFile, phase = phase, **kwargs)

def BuildSpoofaxLibs(basedir, deploy, qualifier, buildStratego, bootstrapStratego, strategoTest, **kwargs):
  phase = 'deploy' if deploy else 'verify'
  pomFile = path.join(basedir, 'spoofax-deploy', 'org.metaborg.maven.build.spoofax.libs', 'pom.xml')
  Mvn(pomFile = pomFile, phase = phase, **kwargs)

def BuildTestRunner(basedir, deploy, qualifier, buildStratego, bootstrapStratego, strategoTest, **kwargs):
  phase = 'deploy' if deploy else 'verify'
  pomFile = path.join(basedir, 'spoofax-deploy', 'org.metaborg.maven.build.spoofax.testrunner', 'pom.xml')
  Mvn(pomFile = pomFile, phase = phase, **kwargs)


'''Build dependencies must be topologically ordered, otherwise the algorithm will not work'''
_buildDependencies = OrderedDict([
  ('poms'        , []),
  ('strategoxt'  , ['poms']),
  ('java'        , ['poms', 'strategoxt']),
  ('eclipse'     , ['poms', 'strategoxt', 'java']),
  ('pluginpoms'  , ['poms', 'strategoxt', 'java', 'eclipse']),
  ('spoofax-libs', ['poms', 'strategoxt', 'java']),
  ('test-runner' , ['poms', 'strategoxt', 'java']),
])
_buildCommands = {
  'poms'         : BuildPoms,
  'strategoxt'   : BuildOrDownloadStrategoXt,
  'java'         : BuildJava,
  'eclipse'      : BuildEclipse,
  'pluginpoms'   : BuildPluginPoms,
  'spoofax-libs' : BuildSpoofaxLibs,
  'test-runner'  : BuildTestRunner,
}

def GetAllBuilds():
  return list(_buildDependencies.keys()) + ['all']

def GetBuildOrder(args):
  if 'all' in args:
    return list(_buildDependencies.keys())

  builds = set()
  for name, deps in _buildDependencies.items():
    if name in args:
      builds.add(name)
      for dep in deps:
        builds.add(dep)
  orderedBuilds = []
  for name in _buildDependencies.keys():
    if name in builds:
      orderedBuilds.append(name)
  return orderedBuilds

def GetBuildCommand(build):
  return _buildCommands[build]


def CreateQualifier(repo):
  date = LatestDate(repo)
  qualifier = date.strftime('%Y%m%d-%H%M%S')
  return qualifier

def CleanLocalRepo():
  print('Cleaning artifacts from local repository')
  localRepo = path.join(path.expanduser('~'), '.m2', 'repository')
  metaborgPath = path.join(localRepo, 'org', 'metaborg')
  print('Deleting {}'.format(metaborgPath))
  shutil.rmtree(metaborgPath, ignore_errors = True)
  cachePath = path.join(localRepo, '.cache', 'tycho')
  print('Deleting {}'.format(cachePath))
  shutil.rmtree(cachePath, ignore_errors = True)


_mvnSettingsLocation = MvnUserSettingsLocation()
_metaborgReleases = 'http://download.spoofax.org/update/artifacts/releases/'
_metaborgSnapshots = None
_spoofaxUpdateSite = 'http://download.spoofax.org/update/nightly/'
_centralMirror = None

def GenerateMavenSettings(location = _mvnSettingsLocation, metaborgReleases = _metaborgReleases,
    metaborgSnapshots = _metaborgSnapshots, spoofaxUpdateSite = _spoofaxUpdateSite, centralMirror = _centralMirror):
  repositories = []
  if metaborgReleases:
    repositories.append(('add-metaborg-repositories', 'metaborg-nexus-releases', metaborgReleases, None, True, False, True))
  if metaborgSnapshots:
    repositories.append(('add-metaborg-repositories', 'metaborg-nexus-snapshots', metaborgSnapshots, None, True, False, True))
  if spoofaxUpdateSite:
    repositories.append(('add-metaborg-repositories', 'spoofax-nightly', spoofaxUpdateSite, 'p2', False, False, False))

  mirrors = []
  if centralMirror:
    mirrors.append(('metaborg-nexus-central-mirror', centralMirror, 'central'))

  MvnSetingsGen(location = location, repositories = repositories, mirrors = mirrors)
