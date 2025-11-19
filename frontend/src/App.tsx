import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import { QueryClient, QueryClientProvider } from 'react-query';

import Layout from './components/Layout';
import Home from './pages/Home';
import WorldView from './pages/WorldView';
import Character from './pages/Character';
import PlotOutline from './pages/PlotOutline';
import ChapterOutline from './pages/ChapterOutline';
import Events from './pages/Events';
import DetailedPlot from './pages/DetailedPlot';

import './App.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <ConfigProvider locale={zhCN}>
        <Router>
          <Layout>
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/world" element={<WorldView />} />
              <Route path="/character" element={<Character />} />
              <Route path="/plot-outline" element={<PlotOutline />} />
              <Route path="/chapter-outline" element={<ChapterOutline />} />
              <Route path="/events" element={<Events />} />
              <Route path="/detailed-plot" element={<DetailedPlot />} />
            </Routes>
          </Layout>
        </Router>
      </ConfigProvider>
    </QueryClientProvider>
  );
};

export default App;
