import React, { useState, useEffect, useRef } from 'react';
import { 
  Activity, 
  Zap, 
  DollarSign, 
  Users, 
  TrendingUp, 
  AlertTriangle, 
  CheckCircle, 
  XCircle, 
  BarChart3, 
  PieChart, 
  Settings, 
  Monitor, 
  Database,
  Network,
  Cpu,
  Cloud,
  // Removed unused imports: Shield, Brain, Layers, Globe, Timer
} from 'lucide-react';

const MultiLLMOrchestrationPlatform = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [metrics, setMetrics] = useState({
    totalRequests: 156789,
    avgResponseTime: 234,
    costSavings: 34.7,
    activeProviders: 5,
    successRate: 99.2,
    costPerRequest: 0.0087
  });

  const [llmProviders] = useState([
    { 
      name: 'OpenAI GPT-4', 
      status: 'active', 
      responseTime: 245, 
      cost: 0.03, 
      requests: 45234,
      marketShare: 42.1,
      reliability: 99.1
    },
    { 
      name: 'Anthropic Claude', 
      status: 'active', 
      responseTime: 189, 
      cost: 0.025, 
      requests: 38967,
      marketShare: 25.2,
      reliability: 99.4
    },
    { 
      name: 'Google Gemini', 
      status: 'active', 
      responseTime: 167, 
      cost: 0.022, 
      requests: 32145,
      marketShare: 18.7,
      reliability: 98.9
    },
    { 
      name: 'Microsoft Copilot', 
      status: 'degraded', 
      responseTime: 312, 
      cost: 0.028, 
      requests: 21456,
      marketShare: 9.3,
      reliability: 97.8
    },
    { 
      name: 'Meta LLaMA', 
      status: 'active', 
      responseTime: 201, 
      cost: 0.018, 
      requests: 19187,
      marketShare: 4.7,
      reliability: 98.2
    }
  ]);

  const canvasRef = useRef(null);

  // Fixed useEffect dependency array
  useEffect(() => {
    const interval = setInterval(() => {
      setMetrics(prev => ({
        ...prev,
        totalRequests: prev.totalRequests + Math.floor(Math.random() * 50),
        avgResponseTime: 200 + Math.floor(Math.random() * 100),
        successRate: 98.5 + Math.random() * 1.5,
        costPerRequest: 0.008 + Math.random() * 0.004
      }));
    }, 2000);

    return () => clearInterval(interval);
  }, []); // Dependencies removed since we're only updating state

  // Network visualization with Canvas
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    
    let animationFrame;
    let time = 0;

    const drawNetwork = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      // Central orchestration hub
      const hubRadius = 30 + Math.sin(time * 0.05) * 5;
      ctx.beginPath();
      ctx.arc(centerX, centerY, hubRadius, 0, 2 * Math.PI);
      ctx.fillStyle = `rgba(59, 130, 246, ${0.8 + Math.sin(time * 0.1) * 0.2})`;
      ctx.fill();
      ctx.strokeStyle = '#3b82f6';
      ctx.lineWidth = 2;
      ctx.stroke();

      // Provider nodes
      llmProviders.forEach((provider, index) => {
        const angle = (index * 2 * Math.PI) / llmProviders.length + time * 0.02;
        const radius = 120 + Math.sin(time * 0.03 + index) * 20;
        const x = centerX + Math.cos(angle) * radius;
        const y = centerY + Math.sin(angle) * radius;
        
        // Connection lines with pulse effect
        ctx.beginPath();
        ctx.moveTo(centerX, centerY);
        ctx.lineTo(x, y);
        ctx.strokeStyle = `rgba(34, 197, 94, ${0.3 + Math.sin(time * 0.1 + index) * 0.3})`;
        ctx.lineWidth = 2;
        ctx.stroke();

        // Provider nodes
        const nodeRadius = provider.status === 'active' ? 20 : 15;
        ctx.beginPath();
        ctx.arc(x, y, nodeRadius, 0, 2 * Math.PI);
        ctx.fillStyle = provider.status === 'active' ? 
          `rgba(34, 197, 94, ${0.7 + Math.sin(time * 0.08 + index) * 0.3})` : 
          'rgba(239, 68, 68, 0.7)';
        ctx.fill();
        ctx.strokeStyle = provider.status === 'active' ? '#22c55e' : '#ef4444';
        ctx.lineWidth = 2;
        ctx.stroke();

        // Provider labels
        ctx.fillStyle = '#e5e7eb';
        ctx.font = '12px Inter, sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(provider.name.split(' ')[0], x, y - nodeRadius - 10);
      });

      // Data flow particles
      for (let i = 0; i < 8; i++) {
        const particleAngle = (time * 0.1 + i * 0.5) % (2 * Math.PI);
        const particleRadius = 40 + (time * 2 + i * 20) % 100;
        const px = centerX + Math.cos(particleAngle) * particleRadius;
        const py = centerY + Math.sin(particleAngle) * particleRadius;
        
        ctx.beginPath();
        ctx.arc(px, py, 3, 0, 2 * Math.PI);
        ctx.fillStyle = `rgba(168, 85, 247, ${1 - (particleRadius - 40) / 100})`;
        ctx.fill();
      }

      time++;
      animationFrame = requestAnimationFrame(drawNetwork);
    };

    drawNetwork();
    return () => cancelAnimationFrame(animationFrame);
  }, [llmProviders]); // Added llmProviders as dependency

  // Removed unused getCongressionProviders function

  const getCongressionalAnalysis = () => ({
    marketConcentration: 67.3,
    competitionScore: 88.4,
    switchingCosts: 156000,
    vendorDiversity: 82,
    recommendations: [
      "Mandate multi-provider architecture for government AI contracts",
      "Establish API standardization requirements",
      "Create switching cost transparency requirements",
      "Fund open-source AI development initiatives",
      "Implement regular competition audits",
      "Establish AI market concentration thresholds"
    ]
  });

  const renderOverview = () => (
    <div className="space-y-6">
      {/* Real-time Network Visualization */}
      <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700/50">
        <h3 className="text-xl font-semibold mb-4 text-white flex items-center">
          <Network className="mr-2 text-blue-400" size={24} />
          Live AI Provider Network
        </h3>
        <div className="flex justify-center">
          <canvas 
            ref={canvasRef} 
            width={600} 
            height={400} 
            className="border border-gray-600/50 rounded-lg bg-gray-900/30"
          />
        </div>
        <div className="mt-4 text-center text-gray-300">
          <p className="text-sm">Real-time orchestration across {llmProviders.length} AI providers</p>
        </div>
      </div>

      {/* Key Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="bg-gradient-to-br from-blue-900/40 to-blue-800/20 backdrop-blur-sm rounded-xl p-6 border border-blue-700/30">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-200 text-sm font-medium">Total Requests</p>
              <p className="text-2xl font-bold text-white">{metrics.totalRequests.toLocaleString()}</p>
            </div>
            <Activity className="text-blue-400" size={32} />
          </div>
          <div className="mt-2">
            <span className="text-green-400 text-sm font-medium">↗ 12.3% from last hour</span>
          </div>
        </div>

        <div className="bg-gradient-to-br from-green-900/40 to-green-800/20 backdrop-blur-sm rounded-xl p-6 border border-green-700/30">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-green-200 text-sm font-medium">Avg Response Time</p>
              <p className="text-2xl font-bold text-white">{metrics.avgResponseTime}ms</p>
            </div>
            <Zap className="text-green-400" size={32} />
          </div>
          <div className="mt-2">
            <span className="text-green-400 text-sm font-medium">↗ 8.7% improvement</span>
          </div>
        </div>

        <div className="bg-gradient-to-br from-purple-900/40 to-purple-800/20 backdrop-blur-sm rounded-xl p-6 border border-purple-700/30">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-purple-200 text-sm font-medium">Cost Savings</p>
              <p className="text-2xl font-bold text-white">{metrics.costSavings}%</p>
            </div>
            <DollarSign className="text-purple-400" size={32} />
          </div>
          <div className="mt-2">
            <span className="text-green-400 text-sm font-medium">$47K saved this month</span>
          </div>
        </div>
      </div>

      {/* Provider Status Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {llmProviders.map((provider, index) => (
          <div key={index} className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700/50">
            <div className="flex items-center justify-between mb-4">
              <h4 className="text-lg font-semibold text-white">{provider.name}</h4>
              <div className="flex items-center">
                {provider.status === 'active' ? (
                  <CheckCircle className="text-green-400 mr-2" size={20} />
                ) : (
                  <XCircle className="text-red-400 mr-2" size={20} />
                )}
                <span className={`text-sm font-medium ${
                  provider.status === 'active' ? 'text-green-400' : 'text-red-400'
                }`}>
                  {provider.status.charAt(0).toUpperCase() + provider.status.slice(1)}
                </span>
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-gray-400">Response Time</p>
                <p className="text-white font-medium">{provider.responseTime}ms</p>
              </div>
              <div>
                <p className="text-gray-400">Cost per 1K tokens</p>
                <p className="text-white font-medium">${provider.cost}</p>
              </div>
              <div>
                <p className="text-gray-400">Requests (24h)</p>
                <p className="text-white font-medium">{provider.requests.toLocaleString()}</p>
              </div>
              <div>
                <p className="text-gray-400">Reliability</p>
                <p className="text-white font-medium">{provider.reliability}%</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderAnalytics = () => (
    <div className="space-y-6">
      <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700/50">
        <h3 className="text-xl font-semibold mb-6 text-white flex items-center">
          <BarChart3 className="mr-2 text-blue-400" size={24} />
          Performance Analytics
        </h3>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Market Share Chart */}
          <div>
            <h4 className="text-lg font-medium text-white mb-4">Market Share Distribution</h4>
            <div className="space-y-3">
              {llmProviders.map((provider, index) => (
                <div key={index} className="flex items-center justify-between">
                  <span className="text-gray-300">{provider.name}</span>
                  <div className="flex items-center w-32">
                    <div className="w-20 bg-gray-700 rounded-full h-2 mr-2">
                      <div 
                        className="bg-blue-500 h-2 rounded-full" 
                        style={{width: `${provider.marketShare * 2}%`}}
                      ></div>
                    </div>
                    <span className="text-white text-sm">{provider.marketShare}%</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Cost Analysis */}
          <div>
            <h4 className="text-lg font-medium text-white mb-4">Cost Optimization Impact</h4>
            <div className="space-y-4">
              <div className="bg-gradient-to-r from-green-900/30 to-green-800/30 rounded-lg p-4">
                <p className="text-green-300 text-sm">Monthly Savings</p>
                <p className="text-2xl font-bold text-white">$47,892</p>
                <p className="text-green-400 text-sm">↗ 34.7% cost reduction</p>
              </div>
              <div className="bg-gradient-to-r from-blue-900/30 to-blue-800/30 rounded-lg p-4">
                <p className="text-blue-300 text-sm">Avg Cost per Request</p>
                <p className="text-2xl font-bold text-white">${metrics.costPerRequest.toFixed(4)}</p>
                <p className="text-blue-400 text-sm">Across all providers</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderCongressional = () => {
    const analysis = getCongressionalAnalysis();
    
    return (
      <div className="space-y-6">
        <div className="bg-gradient-to-br from-red-900/20 to-blue-900/20 backdrop-blur-sm rounded-xl p-6 border border-gray-700/50">
          <h3 className="text-xl font-semibold mb-6 text-white flex items-center">
            <Users className="mr-2 text-red-400" size={24} />
            Congressional Antitrust Analysis
          </h3>
          
          {/* Market Concentration Alert */}
          <div className="bg-red-900/30 border border-red-700/50 rounded-lg p-4 mb-6">
            <div className="flex items-center">
              <AlertTriangle className="text-red-400 mr-3" size={24} />
              <div>
                <h4 className="text-red-300 font-semibold">High Market Concentration Detected</h4>
                <p className="text-red-200 text-sm">Top 2 providers control {analysis.marketConcentration}% of the market</p>
              </div>
            </div>
          </div>

          {/* Key Metrics Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <div className="bg-gray-800/50 rounded-lg p-4">
              <p className="text-gray-400 text-sm">Market Concentration</p>
              <p className="text-2xl font-bold text-red-400">{analysis.marketConcentration}%</p>
              <p className="text-red-300 text-xs">Top 2 providers</p>
            </div>
            <div className="bg-gray-800/50 rounded-lg p-4">
              <p className="text-gray-400 text-sm">Competition Score</p>
              <p className="text-2xl font-bold text-green-400">{analysis.competitionScore}</p>
              <p className="text-green-300 text-xs">With orchestration</p>
            </div>
            <div className="bg-gray-800/50 rounded-lg p-4">
              <p className="text-gray-400 text-sm">Avg Switching Cost</p>
              <p className="text-2xl font-bold text-yellow-400">${(analysis.switchingCosts/1000).toFixed(0)}K</p>
              <p className="text-yellow-300 text-xs">Per enterprise</p>
            </div>
            <div className="bg-gray-800/50 rounded-lg p-4">
              <p className="text-gray-400 text-sm">Vendor Diversity</p>
              <p className="text-2xl font-bold text-blue-400">{analysis.vendorDiversity}%</p>
              <p className="text-blue-300 text-xs">Improvement</p>
            </div>
          </div>

          {/* Policy Recommendations */}
          <div>
            <h4 className="text-lg font-semibold text-white mb-4">Congressional Action Items</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {analysis.recommendations.map((rec, index) => (
                <div key={index} className="bg-gray-800/50 rounded-lg p-4 border-l-4 border-blue-500">
                  <p className="text-gray-300 text-sm">{rec}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  };

  const renderOptimization = () => (
    <div className="space-y-6">
      <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700/50">
        <h3 className="text-xl font-semibold mb-6 text-white flex items-center">
          <TrendingUp className="mr-2 text-green-400" size={24} />
          Cost Optimization Engine
        </h3>
        
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <h4 className="text-lg font-medium text-white mb-4">Optimization Strategies</h4>
            <div className="space-y-4">
              <div className="bg-green-900/30 rounded-lg p-4 border border-green-700/50">
                <h5 className="text-green-300 font-medium">Smart Load Balancing</h5>
                <p className="text-gray-300 text-sm mt-1">Route requests to lowest-cost providers based on real-time pricing</p>
                <p className="text-green-400 text-sm font-medium mt-2">Savings: 23.4%</p>
              </div>
              
              <div className="bg-blue-900/30 rounded-lg p-4 border border-blue-700/50">
                <h5 className="text-blue-300 font-medium">Bulk Request Optimization</h5>
                <p className="text-gray-300 text-sm mt-1">Batch similar requests to take advantage of volume discounts</p>
                <p className="text-blue-400 text-sm font-medium mt-2">Savings: 18.7%</p>
              </div>
              
              <div className="bg-purple-900/30 rounded-lg p-4 border border-purple-700/50">
                <h5 className="text-purple-300 font-medium">Failover Cost Management</h5>
                <p className="text-gray-300 text-sm mt-1">Minimize premium tier usage during provider outages</p>
                <p className="text-purple-400 text-sm font-medium mt-2">Savings: 11.2%</p>
              </div>
            </div>
          </div>
          
          <div>
            <h4 className="text-lg font-medium text-white mb-4">Monthly Impact</h4>
            <div className="space-y-4">
              <div className="text-center bg-gradient-to-br from-green-900/40 to-green-800/20 rounded-lg p-6">
                <p className="text-green-200 text-sm">Total Savings</p>
                <p className="text-3xl font-bold text-white">$47.9K</p>
                <p className="text-green-400 text-sm">This month</p>
              </div>
              
              <div className="text-center bg-gradient-to-br from-blue-900/40 to-blue-800/20 rounded-lg p-6">
                <p className="text-blue-200 text-sm">Cost Reduction</p>
                <p className="text-3xl font-bold text-white">34.7%</p>
                <p className="text-blue-400 text-sm">vs single provider</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderSettings = () => (
    <div className="space-y-6">
      <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700/50">
        <h3 className="text-xl font-semibold mb-6 text-white flex items-center">
          <Settings className="mr-2 text-gray-400" size={24} />
          Platform Configuration
        </h3>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div>
            <h4 className="text-lg font-medium text-white mb-4">Provider Management</h4>
            <div className="space-y-4">
              {llmProviders.map((provider, index) => (
                <div key={index} className="bg-gray-700/50 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-white font-medium">{provider.name}</span>
                    <div className="flex items-center space-x-2">
                      <button className="px-3 py-1 bg-blue-600 text-white text-xs rounded">Configure</button>
                      <button className="px-3 py-1 bg-gray-600 text-white text-xs rounded">
                        {provider.status === 'active' ? 'Disable' : 'Enable'}
                      </button>
                    </div>
                  </div>
                  <div className="text-sm text-gray-300">
                    <p>Priority: {index + 1} | Weight: {(100 - index * 15)}%</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
          
          <div>
            <h4 className="text-lg font-medium text-white mb-4">System Health</h4>
            <div className="space-y-4">
              <div className="bg-gray-700/50 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-white">API Gateway</span>
                  <CheckCircle className="text-green-400" size={20} />
                </div>
                <p className="text-sm text-gray-300">All endpoints responding</p>
              </div>
              
              <div className="bg-gray-700/50 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-white">Load Balancer</span>
                  <CheckCircle className="text-green-400" size={20} />
                </div>
                <p className="text-sm text-gray-300">Optimal distribution active</p>
              </div>
              
              <div className="bg-gray-700/50 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-white">Cost Monitor</span>
                  <CheckCircle className="text-green-400" size={20} />
                </div>
                <p className="text-sm text-gray-300">Within budget thresholds</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const tabs = [
    { id: 'overview', label: 'Overview', icon: Monitor },
    { id: 'analytics', label: 'Analytics', icon: BarChart3 },
    { id: 'congressional', label: 'Congressional Oversight', icon: Users },
    { id: 'optimization', label: 'Cost Optimization', icon: TrendingUp },
    { id: 'settings', label: 'Settings', icon: Settings }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">
            Multi-LLM Orchestration Platform
          </h1>
          <p className="text-gray-300 text-lg">
            Intelligent AI Provider Management & Congressional Oversight Dashboard
          </p>
          <p className="text-gray-400 text-sm mt-2">
            Built by Joseph Bidias for Healthcare AI Governance & Vendor Lock-in Prevention
          </p>
        </div>

        {/* Navigation Tabs */}
        <div className="flex flex-wrap justify-center mb-8 bg-gray-800/30 backdrop-blur-sm rounded-xl p-2">
          {tabs.map((tab) => {
            const IconComponent = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center px-4 py-2 mx-1 my-1 rounded-lg transition-all duration-200 ${
                  activeTab === tab.id
                    ? 'bg-blue-600 text-white shadow-lg'
                    : 'text-gray-300 hover:bg-gray-700/50 hover:text-white'
                }`}
              >
                <IconComponent size={18} className="mr-2" />
                <span className="font-medium">{tab.label}</span>
              </button>
            );
          })}
        </div>

        {/* Tab Content */}
        <div className="transition-all duration-300">
          {activeTab === 'overview' && renderOverview()}
          {activeTab === 'analytics' && renderAnalytics()}
          {activeTab === 'congressional' && renderCongressional()}
          {activeTab === 'optimization' && renderOptimization()}
          {activeTab === 'settings' && renderSettings()}
        </div>

        {/* Footer */}
        <div className="text-center mt-12 pt-8 border-t border-gray-700/50">
          <p className="text-gray-400 text-sm">
            © 2025 Joseph Bidias | Multi-LLM Orchestration Platform | 
            <a href="mailto:aiglevision35@gmail.com" className="text-blue-400 hover:text-blue-300 ml-1">
              aiglevision35@gmail.com
            </a>
          </p>
          <p className="text-gray-500 text-xs mt-1">
            Advancing AI governance through intelligent provider orchestration
          </p>
        </div>
      </div>
    </div>
  );
};

export default MultiLLMOrchestrationPlatform;
