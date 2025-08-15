import React, { useState, useEffect } from 'react';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, 
  LineChart, Line, PieChart, Pie, Cell, ResponsiveContainer 
} from 'recharts';
import { 
  Phone, TrendingUp, Users, CreditCard, Activity, 
  Play, BarChart3, Settings, Bell, Download 
} from 'lucide-react';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

const PresentationDashboard = () => {
  const [stats, setStats] = useState({
    callsToday: 0,
    successRate: 0,
    dueEmis: 0,
    collections: 0
  });
  
  const [liveData, setLiveData] = useState([]);
  const [isLiveDemo, setIsLiveDemo] = useState(false);
  const [demoStep, setDemoStep] = useState(0);
  
  // Mock data for charts
  const performanceData = [
    { name: 'Mon', calls: 120, successful: 100 },
    { name: 'Tue', calls: 190, successful: 150 },
    { name: 'Wed', calls: 300, successful: 250 },
    { name: 'Thu', calls: 500, successful: 420 },
    { name: 'Fri', calls: 200, successful: 180 },
    { name: 'Sat', calls: 300, successful: 270 },
    { name: 'Sun', calls: 450, successful: 380 }
  ];
  
  const collectionData = [
    { name: 'Collected', value: 65, color: '#00C49F' },
    { name: 'Pending', value: 25, color: '#FFBB28' },
    { name: 'Overdue', value: 10, color: '#FF8042' }
  ];
  
  const demoSteps = [
    'Initializing AI agents...',
    'Scanning database for due EMIs...',
    'Analyzing customer risk profiles...',
    'Initiating AI voice calls...',
    'Processing customer responses...',
    'Making intelligent decisions...',
    'Generating payment links...',
    'Updating analytics and learning models...',
    'Demo completed successfully! 🎉'
  ];

  useEffect(() => {
    // Simulate real-time data updates
    const interval = setInterval(() => {
      setStats(prev => ({
        callsToday: prev.callsToday + Math.floor(Math.random() * 5),
        successRate: 73 + Math.random() * 10,
        dueEmis: Math.max(0, prev.dueEmis - Math.floor(Math.random() * 3)),
        collections: prev.collections + Math.floor(Math.random() * 50000)
      }));
    }, 5000);
    
    return () => clearInterval(interval);
  }, []);

  const runLiveDemo = () => {
    setIsLiveDemo(true);
    setDemoStep(0);
    
    const stepInterval = setInterval(() => {
      setDemoStep(prev => {
        if (prev >= demoSteps.length - 1) {
          clearInterval(stepInterval);
          setTimeout(() => setIsLiveDemo(false), 2000);
          return prev;
        }
        return prev + 1;
      });
    }, 2000);
  };

  const StatCard = ({ icon: Icon, title, value, change, color }) => (
    <div className="bg-white rounded-2xl p-6 shadow-lg hover:shadow-xl transition-all duration-300">
      <div className="flex items-center justify-between">
        <div>
          <div className={`p-3 rounded-full ${color} mb-4`}>
            <Icon className="h-6 w-6 text-white" />
          </div>
          <h3 className="text-2xl font-bold text-gray-800">{value}</h3>
          <p className="text-gray-600 text-sm">{title}</p>
          {change && (
            <p className={`text-sm mt-2 ${change.includes('+') ? 'text-green-600' : 'text-red-600'}`}>
              {change}
            </p>
          )}
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-900 via-blue-800 to-indigo-900">
      {/* Navigation Bar */}
      <nav className="bg-white/10 backdrop-blur-md border-b border-white/20 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Activity className="h-8 w-8 text-white" />
            <h1 className="text-2xl font-bold text-white">EMI VoiceBot</h1>
          </div>
          
          <div className="flex items-center space-x-4">
            <button className="bg-white/20 hover:bg-white/30 text-white px-4 py-2 rounded-lg transition-colors">
              <Settings className="h-5 w-5" />
            </button>
            <button className="bg-white/20 hover:bg-white/30 text-white px-4 py-2 rounded-lg transition-colors">
              <Bell className="h-5 w-5" />
            </button>
          </div>
        </div>
      </nav>

      <div className="p-6">
        {/* Header */}
        <div className="bg-white rounded-2xl p-8 mb-6 shadow-xl">
          <h2 className="text-3xl font-bold text-gray-800 mb-2">
            AI-Powered EMI Collection Dashboard
          </h2>
          <p className="text-gray-600">
            Real-time monitoring and control of automated EMI collection system
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatCard
            icon={Phone}
            title="Calls Today"
            value={stats.callsToday || 247}
            change="+12% from yesterday"
            color="bg-blue-500"
          />
          <StatCard
            icon={TrendingUp}
            title="Success Rate"
            value={`${stats.successRate.toFixed(1) || 73}%`}
            change="+5.2% this week"
            color="bg-green-500"
          />
          <StatCard
            icon={Users}
            title="Due EMIs"
            value={stats.dueEmis || 156}
            change="-8% from last week"
            color="bg-yellow-500"
          />
          <StatCard
            icon={CreditCard}
            title="Collections"
            value={`₹${((stats.collections || 2450000) / 100000).toFixed(1)}L`}
            change="+18% this month"
            color="bg-purple-500"
          />
        </div>

        {/* Action Buttons */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <button className="bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white px-6 py-4 rounded-xl transition-all duration-300 transform hover:scale-105 shadow-lg">
            <div className="flex items-center justify-center space-x-2">
              <Phone className="h-5 w-5" />
              <span>Check Due EMIs</span>
            </div>
          </button>
          
          <button 
            onClick={runLiveDemo}
            className="bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 text-white px-6 py-4 rounded-xl transition-all duration-300 transform hover:scale-105 shadow-lg"
          >
            <div className="flex items-center justify-center space-x-2">
              <Play className="h-5 w-5" />
              <span>Start Live Demo</span>
            </div>
          </button>
          
          <button className="bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-700 hover:to-purple-800 text-white px-6 py-4 rounded-xl transition-all duration-300 transform hover:scale-105 shadow-lg">
            <div className="flex items-center justify-center space-x-2">
              <BarChart3 className="h-5 w-5" />
              <span>View Analytics</span>
            </div>
          </button>
          
          <button className="bg-gradient-to-r from-indigo-600 to-indigo-700 hover:from-indigo-700 hover:to-indigo-800 text-white px-6 py-4 rounded-xl transition-all duration-300 transform hover:scale-105 shadow-lg">
            <div className="flex items-center justify-center space-x-2">
              <Download className="h-5 w-5" />
              <span>Export Report</span>
            </div>
          </button>
        </div>

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* Performance Chart */}
          <div className="lg:col-span-2 bg-white rounded-2xl p-6 shadow-xl">
            <h3 className="text-xl font-bold text-gray-800 mb-4">Call Performance Trends</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={performanceData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="calls" stroke="#8884d8" strokeWidth={2} />
                <Line type="monotone" dataKey="successful" stroke="#82ca9d" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Collection Distribution */}
          <div className="bg-white rounded-2xl p-6 shadow-xl">
            <h3 className="text-xl font-bold text-gray-800 mb-4">Collection Distribution</h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={collectionData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, value }) => `${name}: ${value}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {collectionData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Live Demo Modal */}
        {isLiveDemo && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
            <div className="bg-white rounded-2xl p-8 max-w-md w-full mx-4 shadow-2xl">
              <h3 className="text-2xl font-bold text-gray-800 mb-6">🎭 Live Demo in Progress</h3>
              
              <div className="space-y-4">
                {demoSteps.slice(0, demoStep + 1).map((step, index) => (
                  <div 
                    key={index}
                    className={`p-4 rounded-lg border-l-4 transition-all duration-500 ${
                      index === demoStep 
                        ? 'bg-blue-50 border-blue-500 text-blue-800' 
                        : 'bg-gray-50 border-gray-300 text-gray-600'
                    }`}
                  >
                    <div className="flex items-center space-x-3">
                      <span className="font-semibold">{index + 1}.</span>
                      <span>{step}</span>
                      {index === demoStep && (
                        <div className="animate-spin h-4 w-4 border-2 border-blue-500 border-t-transparent rounded-full"></div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
              
              <div className="mt-6">
                <div className="bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full transition-all duration-500"
                    style={{ width: `${((demoStep + 1) / demoSteps.length) * 100}%` }}
                  ></div>
                </div>
                <p className="text-sm text-gray-600 mt-2 text-center">
                  Progress: {demoStep + 1} of {demoSteps.length}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Activity Log */}
        <div className="bg-white rounded-2xl p-6 shadow-xl">
          <h3 className="text-xl font-bold text-gray-800 mb-4">System Activity Log</h3>
          <div className="bg-gray-900 text-green-400 p-4 rounded-lg font-mono text-sm max-h-60 overflow-y-auto">
            <div>[12:45:23] System initialized and ready</div>
            <div>[12:45:45] Checking for due EMIs...</div>
            <div>[12:45:47] Found 156 customers requiring calls</div>
            <div>[12:46:02] AI voice call initiated for customer CUST_12345</div>
            <div>[12:46:15] Customer response analyzed: Payment commitment received</div>
            <div>[12:46:18] Payment link generated and sent</div>
            <div>[12:46:32] Analytics model updated with new interaction data</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PresentationDashboard;
