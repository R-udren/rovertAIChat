// Performance monitoring utilities
const DEBUG = import.meta.env.DEV

export const perfLogger = {
  timers: new Map(),
  
  start(label) {
    if (!DEBUG) return
    this.timers.set(label, performance.now())
  },
  
  end(label) {
    if (!DEBUG) return
    const start = this.timers.get(label)
    if (start) {
      const duration = performance.now() - start
      console.log(`⏱️ ${label}: ${duration.toFixed(2)}ms`)
      this.timers.delete(label)
      return duration
    }
  },
  
  measure(label, fn) {
    if (!DEBUG) return fn()
    this.start(label)
    const result = fn()
    
    if (result instanceof Promise) {
      return result.finally(() => this.end(label))
    }
    
    this.end(label)
    return result
  }
}

// Route transition performance tracking
export const trackRoutePerformance = (router) => {
  if (!DEBUG) return
  
  router.beforeEach((to, from, next) => {
    perfLogger.start(`Route: ${from.path || '/'} → ${to.path}`)
    next()
  })
  
  router.afterEach((to, from) => {
    perfLogger.end(`Route: ${from.path || '/'} → ${to.path}`)
  })
}
