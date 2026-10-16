package com.netenc.app

import android.app.Activity
import android.app.Application
import android.content.Intent
import android.os.Bundle

/**
 * Re-locks the app when every activity leaves the foreground.
 * Internal navigation stays unlocked while at least one activity remains active.
 */
class NetEncApplication : Application(), Application.ActivityLifecycleCallbacks {
    companion object {
        @Volatile var isAuthenticated: Boolean = false
    }

    private var startedActivities = 0
    private var launchingGate = false

    override fun onCreate() {
        super.onCreate()
        registerActivityLifecycleCallbacks(this)
    }

    override fun onActivityStarted(activity: Activity) {
        startedActivities++
        if (activity !is SplashActivity && !isAuthenticated && !launchingGate) {
            launchingGate = true
            activity.startActivity(
                Intent(activity, SplashActivity::class.java)
                    .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            )
            activity.finish()
        }
    }

    override fun onActivityStopped(activity: Activity) {
        startedActivities = (startedActivities - 1).coerceAtLeast(0)
        if (startedActivities == 0) {
            isAuthenticated = false
            launchingGate = false
        }
    }

    override fun onActivityCreated(activity: Activity, state: Bundle?) = Unit
    override fun onActivityResumed(activity: Activity) = Unit
    override fun onActivityPaused(activity: Activity) = Unit
    override fun onActivitySaveInstanceState(activity: Activity, outState: Bundle) = Unit
    override fun onActivityDestroyed(activity: Activity) = Unit
}
