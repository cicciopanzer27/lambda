import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import { Progress } from './ui/progress';
import { Badge } from './ui/badge';
import { Alert, AlertDescription } from './ui/alert';
import LambdaVisualizerWebSocketClient from '../utils/websocketClient';

const LambdaVisualizer = () => {
    const [expression, setExpression] = useState('λx.x');
    const [isConnected, setIsConnected] = useState(false);
    const [currentJob, setCurrentJob] = useState(null);
    const [jobHistory, setJobHistory] = useState([]);
    const [analysis, setAnalysis] = useState(null);
    const [error, setError] = useState(null);
    const [isProcessing, setIsProcessing] = useState(false);
    
    const wsClient = useRef(null);

    useEffect(() => {
        // Initialize WebSocket connection
        wsClient.current = new LambdaVisualizerWebSocketClient();
        
        // Set up message handlers
        wsClient.current.onMessage('system_update', (data) => {
            if (data.status === 'connected') {
                setIsConnected(true);
                setError(null);
            }
        });

        wsClient.current.onMessage('job_update', (data) => {
            setCurrentJob(data);
            setIsProcessing(data.status === 'running');
            
            if (data.status === 'completed' || data.status === 'failed') {
                setIsProcessing(false);
                setCurrentJob(null);
                
                if (data.status === 'completed') {
                    setJobHistory(prev => [data, ...prev.slice(0, 9)]); // Keep last 10 jobs
                }
            }
        });

        wsClient.current.onMessage('job_completed', (data) => {
            setAnalysis(data.result);
            setJobHistory(prev => [data, ...prev.slice(0, 9)]);
            setIsProcessing(false);
            setCurrentJob(null);
        });

        wsClient.current.onMessage('job_failed', (data) => {
            setError(data.error);
            setIsProcessing(false);
            setCurrentJob(null);
        });

        wsClient.current.onMessage('error', (data) => {
            setError(data.error);
        });

        // Connect to WebSocket
        wsClient.current.connect()
            .then(() => {
                console.log('✅ Connected to Lambda Visualizer');
                wsClient.current.subscribeToJobs();
            })
            .catch(error => {
                console.error('❌ Failed to connect:', error);
                setError('Failed to connect to server');
            });

        // Cleanup on unmount
        return () => {
            if (wsClient.current) {
                wsClient.current.disconnect();
            }
        };
    }, []);

    const handleSubmit = () => {
        if (!expression.trim()) {
            setError('Please enter a lambda expression');
            return;
        }

        if (!isConnected) {
            setError('Not connected to server');
            return;
        }

        setError(null);
        setAnalysis(null);
        setIsProcessing(true);
        
        // Submit job via WebSocket
        wsClient.current.submitJob(expression, {
            duration: 5.0,
            quality: 'medium_quality',
            fps: 30
        });
    };

    const handleExampleClick = (exampleExpression) => {
        setExpression(exampleExpression);
    };

    const examples = [
        { name: 'Identity', expr: 'λx.x', desc: 'Returns its argument unchanged' },
        { name: 'Constant K', expr: 'λx.λy.x', desc: 'Always returns the first argument' },
        { name: 'False', expr: 'λx.λy.y', desc: 'Boolean false representation' },
        { name: 'S Combinator', expr: 'λx.λy.λz.(x z)(y z)', desc: 'Distributive application' },
        { name: 'Church 2', expr: 'λf.λx.f(f x)', desc: 'Church numeral for 2' },
        { name: 'Omega', expr: '(λx.x x)(λx.x x)', desc: 'Non-terminating combinator' }
    ];

    return (
        <div className="max-w-6xl mx-auto p-6 space-y-6">
            <div className="text-center">
                <h1 className="text-4xl font-bold mb-2">Lambda Visualizer</h1>
                <p className="text-gray-600">Real-time lambda calculus analysis and visualization</p>
                
                <div className="flex items-center justify-center gap-4 mt-4">
                    <Badge variant={isConnected ? "default" : "destructive"}>
                        {isConnected ? "🟢 Connected" : "🔴 Disconnected"}
                    </Badge>
                    {isProcessing && (
                        <Badge variant="secondary">
                            ⚡ Processing...
                        </Badge>
                    )}
                </div>
            </div>

            {error && (
                <Alert variant="destructive">
                    <AlertDescription>{error}</AlertDescription>
                </Alert>
            )}

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Input Section */}
                <Card>
                    <CardHeader>
                        <CardTitle>Lambda Expression</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <Textarea
                            value={expression}
                            onChange={(e) => setExpression(e.target.value)}
                            placeholder="Enter lambda expression (e.g., λx.x)"
                            className="min-h-[100px] font-mono"
                        />
                        
                        <Button 
                            onClick={handleSubmit} 
                            disabled={!isConnected || isProcessing}
                            className="w-full"
                        >
                            {isProcessing ? 'Processing...' : 'Analyze & Visualize'}
                        </Button>

                        {currentJob && (
                            <div className="space-y-2">
                                <div className="flex justify-between text-sm">
                                    <span>Progress</span>
                                    <span>{Math.round(currentJob.progress * 100)}%</span>
                                </div>
                                <Progress value={currentJob.progress * 100} />
                                <p className="text-sm text-gray-600">{currentJob.message}</p>
                            </div>
                        )}
                    </CardContent>
                </Card>

                {/* Examples Section */}
                <Card>
                    <CardHeader>
                        <CardTitle>Examples</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="grid grid-cols-1 gap-2">
                            {examples.map((example, index) => (
                                <Button
                                    key={index}
                                    variant="outline"
                                    className="justify-start h-auto p-3"
                                    onClick={() => handleExampleClick(example.expr)}
                                >
                                    <div className="text-left">
                                        <div className="font-mono text-sm">{example.expr}</div>
                                        <div className="text-xs text-gray-500">{example.desc}</div>
                                    </div>
                                </Button>
                            ))}
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* Analysis Results */}
            {analysis && (
                <Card>
                    <CardHeader>
                        <CardTitle>Analysis Results</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-4">
                            <div>
                                <h4 className="font-semibold mb-2">Expression</h4>
                                <p className="font-mono bg-gray-100 p-2 rounded">{analysis.expression}</p>
                            </div>
                            
                            {analysis.beta_reduction && (
                                <div>
                                    <h4 className="font-semibold mb-2">Beta Reduction</h4>
                                    <div className="space-y-2">
                                        <p><strong>Final Term:</strong> <span className="font-mono">{analysis.beta_reduction.final_term}</span></p>
                                        <p><strong>Steps Taken:</strong> {analysis.beta_reduction.steps_taken}</p>
                                        <p><strong>Normal Form:</strong> {analysis.beta_reduction.is_normal_form ? 'Yes' : 'No'}</p>
                                        <p><strong>Strategy:</strong> {analysis.beta_reduction.strategy}</p>
                                    </div>
                                </div>
                            )}

                            {analysis.processing_info && (
                                <div>
                                    <h4 className="font-semibold mb-2">Processing Info</h4>
                                    <div className="flex gap-4">
                                        <Badge variant={analysis.processing_info.gpu_used ? "default" : "secondary"}>
                                            GPU: {analysis.processing_info.gpu_used ? 'Used' : 'Not Available'}
                                        </Badge>
                                        <Badge variant={analysis.processing_info.manim_used ? "default" : "secondary"}>
                                            Manim: {analysis.processing_info.manim_used ? 'Used' : 'Fallback'}
                                        </Badge>
                                        <Badge variant={analysis.processing_info.video_generated ? "default" : "secondary"}>
                                            Video: {analysis.processing_info.video_generated ? 'Generated' : 'Not Generated'}
                                        </Badge>
                                    </div>
                                </div>
                            )}
                        </div>
                    </CardContent>
                </Card>
            )}

            {/* Job History */}
            {jobHistory.length > 0 && (
                <Card>
                    <CardHeader>
                        <CardTitle>Recent Jobs</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-2">
                            {jobHistory.slice(0, 5).map((job, index) => (
                                <div key={index} className="flex items-center justify-between p-2 border rounded">
                                    <div>
                                        <span className="font-mono text-sm">{job.result?.expression || 'Unknown'}</span>
                                        <Badge variant={job.status === 'completed' ? 'default' : 'destructive'} className="ml-2">
                                            {job.status}
                                        </Badge>
                                    </div>
                                    <span className="text-xs text-gray-500">
                                        {new Date(job.timestamp).toLocaleTimeString()}
                                    </span>
                                </div>
                            ))}
                        </div>
                    </CardContent>
                </Card>
            )}
        </div>
    );
};

export default LambdaVisualizer;
