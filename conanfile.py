from conans import ConanFile, tools, Meson
from conanos.build import config_scheme
import os

class LibpslConan(ConanFile):
    name = "libpsl"
    version = "0.20.2"
    description = "C library for the Public Suffix List"
    url = "https://github.com/conanos/libpsl"
    homepage = "https://rockdaboot.github.io/libpsl"
    license = "MIT"
    patch = "msvc-ssize_t.patch"
    exports = ["LICENSE", patch]
    generators = "visual_studio", "gcc"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = { 'shared': True, 'fPIC': True }

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx

        config_scheme(self)

    def source(self):
        url_ = "https://github.com/CentricularK/libpsl.git"
        branch_ = "master"
        git = tools.Git(folder=self.name)
        git.clone(url_, branch=branch_)
        with tools.chdir(self.name):
            self.run('git submodule update --init')
        if self.settings.os == 'Windows':
            tools.patch(patch_file=self.patch)
        os.rename(self.name, self._source_subfolder)


    def build(self):
        prefix = os.path.join(self.build_folder, self._build_subfolder, "install")
        defs = {'prefix' : prefix}
        if self.settings.os == "Linux":
            defs.update({'libdir':'lib'})
        meson = Meson(self)
        meson.configure(defs=defs,source_dir=self._source_subfolder, build_dir=self._build_subfolder)
        meson.build()
        self.run('ninja -C {0} install'.format(meson.build_dir))

    def package(self):
        if self.settings.os == 'Windows':
            tools.mkdir(os.path.join(self.package_folder, "include"))
            self.copy("*",dst=os.path.join(self.package_folder, "include"),src=os.path.join(self.build_folder,self._build_subfolder, "include"))
            tools.mkdir(os.path.join(self.package_folder, "lib","pkgconfig"))
            for suffix in ["exp","lib"]:
                self.copy("*."+suffix,dst=os.path.join(self.package_folder, "lib"),src=os.path.join(self.build_folder,self._build_subfolder, "src"))
            self.copy("psl.pdb",dst=os.path.join(self.package_folder, "lib"),src=os.path.join(self.build_folder,self._build_subfolder, "src"))
            tools.mkdir(os.path.join(self.package_folder, "bin"))
            self.copy("*.dll",dst=os.path.join(self.package_folder, "bin"),src=os.path.join(self.build_folder,self._build_subfolder, "src"))
            self.copy("*.exe",dst=os.path.join(self.package_folder, "bin"),src=os.path.join(self.build_folder,self._build_subfolder, "tools"))
            self.copy("*", dst=os.path.join(self.package_folder, "lib","pkgconfig"), src=os.path.join(self.build_folder,self._build_subfolder,"install","lib","pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

