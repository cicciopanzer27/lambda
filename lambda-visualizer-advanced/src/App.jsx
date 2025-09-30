import React from 'react'
import { Sparkles } from 'lucide-react'
import LambdaVisualizer from './components/LambdaVisualizer'
import './App.css'

function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
      {/* Header */}
      <header className="border-b bg-white/80 dark:bg-slate-900/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <Sparkles className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  Lambda Visualizer Enhanced
                </h1>
                <p className="text-sm text-muted-foreground">
                  Real-time Lambda Calculus Analysis with WebSocket Communication
                </p>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <LambdaVisualizer />
    </div>
  )
}

export default App
