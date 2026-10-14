plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("com.google.devtools.ksp") version "1.9.22-1.0.17"
}

android {
    namespace = "com.netenc.app"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.netenc.app"
        minSdk = 26
        targetSdk = 34
        versionCode = 4
        versionName = "1.0.0"
    }

    sourceSets {
        getByName("main") { assets.srcDir(rootProject.projectDir.parentFile.resolve("shared")) }
    }

    buildTypes {
        release {
            isMinifyEnabled = false
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions {
        jvmTarget = "17"
    }
    buildFeatures {
        viewBinding = true
    }
}

// Generate the offline diagram assets before Android packages assets. This makes a
// direct Android Studio/Gradle build behave like CI, instead of relying on a prior
// manual invocation of the Python generator.
val generateNetworkAllDiagrams by tasks.registering(Exec::class) {
    val repositoryRoot = rootProject.projectDir.parentFile
    workingDir(repositoryRoot)
    val pythonCommand = if (System.getProperty("os.name").startsWith("Windows", ignoreCase = true)) "python" else "python3"
    commandLine(pythonCommand, "scripts/generate_android_diagrams.py")
    inputs.file(repositoryRoot.resolve("scripts/generate_android_diagrams.py"))
    inputs.file(repositoryRoot.resolve("server/core/infographics.py"))
    inputs.files(fileTree(repositoryRoot.resolve("tools/packs")) {
        include("ch01/diagrams/**", "ch02/diagrams/**", "ch03/diagrams/**", "ch09/diagrams/**")
    })
    outputs.dir(repositoryRoot.resolve("android/app/src/main/assets/diagrams"))
    outputs.dir(repositoryRoot.resolve("server/static/diagrams"))
}

val repositoryRoot = rootProject.projectDir.parentFile
val pythonCommand = if (System.getProperty("os.name").startsWith("Windows", ignoreCase = true)) "python" else "python3"

val exportSharedCurriculum by tasks.registering(Exec::class) {
    workingDir(repositoryRoot)
    commandLine(pythonCommand, "scripts/export_android_index.py")
    outputs.file(repositoryRoot.resolve("android/app/src/main/assets/curriculum_index.json.gz"))
    outputs.upToDateWhen { false }
}
val mergeSharedPacks by tasks.registering(Exec::class) {
    dependsOn(exportSharedCurriculum)
    workingDir(repositoryRoot)
    commandLine(pythonCommand, "scripts/merge_content_packs_into_android.py")
    outputs.upToDateWhen { false }
}
val importReferenceLessons by tasks.registering(Exec::class) {
    dependsOn(mergeSharedPacks)
    workingDir(repositoryRoot)
    commandLine(pythonCommand, "scripts/import_networkencyclopedia_reference.py")
    outputs.upToDateWhen { false }
}
val validateSharedRunbooks by tasks.registering(Exec::class) {
    dependsOn(importReferenceLessons)
    workingDir(repositoryRoot)
    commandLine(pythonCommand, "scripts/validate_incident_runbooks.py")
}
val validateJalaliDates by tasks.registering(Exec::class) {
    dependsOn(importReferenceLessons)
    workingDir(repositoryRoot)
    commandLine(pythonCommand, "scripts/validate_jalali_dates.py")
}

tasks.named("preBuild").configure {
    dependsOn(generateNetworkAllDiagrams, validateSharedRunbooks, validateJalaliDates)
}

dependencies {
    implementation("androidx.core:core-ktx:1.12.0")
    implementation("androidx.appcompat:appcompat:1.6.1")
    implementation("com.google.android.material:material:1.11.0")
    implementation("androidx.constraintlayout:constraintlayout:2.1.4")
    implementation("com.squareup.okhttp3:okhttp:4.12.0")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3")
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.7.0")
    implementation("androidx.work:work-runtime-ktx:2.9.0")

    val room = "2.6.1"
    implementation("androidx.room:room-runtime:$room")
    implementation("androidx.room:room-ktx:$room")
    ksp("androidx.room:room-compiler:$room")
}
