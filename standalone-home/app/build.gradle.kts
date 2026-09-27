plugins { id("com.android.application") }

android {
    namespace = "com.otakuhoarder.mushokuhome"
    compileSdk = 36
    defaultConfig {
        applicationId = "com.otakuhoarder.mushokuhome"
        minSdk = 31
        targetSdk = 36
        versionCode = 1
        versionName = "0.1.0"
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
}
