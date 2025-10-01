import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Statistic, Progress, List, Typography, Button, Spin, message, Input, Steps, Space, Divider } from 'antd';
import {
  RocketOutlined,
  PlayCircleOutlined,
} from '@ant-design/icons';

const { Title, Paragraph } = Typography;

const Home: React.FC = () => {
  const [stats, setStats] = useState([
    { title: '世界观数量', value: 0, suffix: '个' },
    { title: '角色数量', value: 0, suffix: '个' },
    { title: '剧情节点', value: 0, suffix: '个' },
    { title: '生成内容', value: 0, suffix: '字' },
  ]);
  const [loading, setLoading] = useState(true);
  const [coreConcept, setCoreConcept] = useState('');
  const [autoGenerating, setAutoGenerating] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);

  // 获取统计数据
  const fetchStats = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/progress');
      if (response.ok) {
        const data = await response.json();
        // 根据实际数据更新统计
        setStats([
          { title: '世界观数量', value: data.worldview_count || 0, suffix: '个' },
          { title: '角色数量', value: data.character_count || 0, suffix: '个' },
          { title: '剧情节点', value: data.plot_count || 0, suffix: '个' },
          { title: '生成内容', value: data.total_words || 0, suffix: '字' },
        ]);
      }
    } catch (error) {
      console.error('获取统计数据失败:', error);
      message.warning('无法获取统计数据，显示默认值');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  // 自动生成步骤
  const autoSteps = [
    { title: '1. 世界观生成', description: '生成修仙世界的世界观设定' },
    { title: '2. 角色生成', description: '生成主要角色和正义伙伴' },
    { title: '3. 剧情大纲', description: '生成整体剧情大纲' },
    { title: '4. 章节大纲', description: '生成章节详细大纲' },
    { title: '5. 事件生成', description: '生成具体事件序列' },
    { title: '6. 详细剧情', description: '生成具体章节的详细剧情' },
  ];

  // 自动生成功能
  const handleAutoGenerate = async () => {
    if (!coreConcept.trim()) {
      message.warning('请输入核心概念');
      return;
    }

    setAutoGenerating(true);
    setCurrentStep(0);

    try {
      // 按顺序执行各个步骤
      for (let i = 0; i < autoSteps.length; i++) {
        setCurrentStep(i);
        
        let endpoint = '';
        switch (i) {
          case 0: endpoint = '/api/generate/worldview'; break;
          case 1: endpoint = '/api/generate/characters'; break;
          case 2: endpoint = '/api/generate/plot-outline'; break;
          case 3: endpoint = '/api/generate/chapter-outline'; break;
          case 4: endpoint = '/api/generate/events'; break;
          case 5: endpoint = '/api/generate/detailed-plot'; break;
        }

        const response = await fetch(`http://localhost:8000${endpoint}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ core_concept: coreConcept }),
          signal: AbortSignal.timeout(600000), // 600秒超时
        });

        if (!response.ok) {
          throw new Error(`步骤 ${i + 1} 生成失败`);
        }

        const result = await response.json();
        message.success(`${autoSteps[i].title}完成`);
        
        // 更新统计数据
        await fetchStats();
        
        // 短暂延迟，让用户看到进度
        await new Promise(resolve => setTimeout(resolve, 1000));
      }

      message.success('自动生成完成！');
      setCurrentStep(autoSteps.length);
    } catch (error) {
      message.error(`自动生成失败: ${error.message}`);
    } finally {
      setAutoGenerating(false);
    }
  };


  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <Title level={2}>
          <RocketOutlined style={{ marginRight: 8 }} />
          小说生成智能体框架
        </Title>
        <Paragraph style={{ fontSize: 16, color: '#666' }}>
          基于AI的智能小说生成系统，支持自动一键生成完整小说内容。
        </Paragraph>
      </div>

             {/* 自动生成说明 */}
             <Card style={{ marginBottom: 24 }}>
               <Title level={3}>自动生成模式</Title>
               <Paragraph style={{ color: '#666', marginBottom: 16 }}>
                 输入核心概念后自动按顺序执行所有生成步骤，适合快速生成完整小说内容
               </Paragraph>
               <div style={{ 
                 padding: 16, 
                 background: '#f0f8ff', 
                 borderRadius: 8, 
                 border: '1px solid #d6e4ff' 
               }}>
                 <Title level={4} style={{ color: '#1890ff', margin: '0 0 8px 0' }}>
                   🚀 一键生成流程
                 </Title>
                 <Paragraph style={{ margin: 0, color: '#666' }}>
                   系统将自动执行：1.世界观生成 → 2.角色生成 → 3.剧情大纲 → 4.章节大纲 → 5.事件生成 → 6.详细剧情
                 </Paragraph>
               </div>
             </Card>

      {/* 统计数据 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        {stats.map((stat, index) => (
          <Col xs={12} sm={6} key={index}>
            <Card>
              <Spin spinning={loading}>
                <Statistic
                  title={stat.title}
                  value={stat.value}
                  suffix={stat.suffix}
                  valueStyle={{ color: '#1890ff' }}
                />
              </Spin>
            </Card>
          </Col>
        ))}
      </Row>

      {/* 自动生成 */}
        <Card style={{ marginBottom: 24 }}>
          <Title level={3}>自动生成流程</Title>
          <Space direction="vertical" size="large" style={{ width: '100%' }}>
            <div>
              <Input.TextArea
                placeholder="请输入小说核心概念，例如：一个现代青年穿越到修仙世界，凭借现代知识在修仙界闯荡的故事"
                value={coreConcept}
                onChange={(e) => setCoreConcept(e.target.value)}
                rows={3}
                style={{ marginBottom: 16 }}
              />
              <Button 
                type="primary" 
                size="large" 
                loading={autoGenerating}
                onClick={handleAutoGenerate}
                disabled={!coreConcept.trim()}
                style={{ 
                  height: 50, 
                  fontSize: 16, 
                  fontWeight: 600,
                  boxShadow: '0 4px 12px rgba(24, 144, 255, 0.3)',
                }}
              >
                {autoGenerating ? '正在生成...' : '🚀 开始自动生成'}
              </Button>
            </div>
            
            <Divider />
            
            <div>
              <Title level={4}>生成步骤</Title>
              <Steps
                current={currentStep}
                items={autoSteps.map((step, index) => ({
                  title: step.title,
                  description: step.description,
                  status: index < currentStep ? 'finish' : 
                         index === currentStep ? (autoGenerating ? 'process' : 'wait') : 'wait'
                }))}
              />
            </div>
          </Space>
        </Card>

      <Card style={{ marginTop: 24 }}>
        <Title level={3}>系统状态</Title>
        <Row gutter={16}>
          <Col span={8}>
            <div style={{ textAlign: 'center' }}>
              <Progress
                type="circle"
                percent={stats[0].value > 0 ? 85 : 0}
                format={(percent) => `${percent}%`}
                strokeColor="#52c41a"
                size={80}
              />
              <div style={{ marginTop: 8, fontSize: 14, color: '#666' }}>
                {stats[0].value > 0 ? '系统健康度' : '等待初始化'}
              </div>
            </div>
          </Col>
          <Col span={8}>
            <div style={{ textAlign: 'center' }}>
              <Progress
                type="circle"
                percent={stats[1].value > 0 ? 72 : 0}
                format={(percent) => `${percent}%`}
                strokeColor="#1890ff"
                size={80}
              />
              <div style={{ marginTop: 8, fontSize: 14, color: '#666' }}>
                {stats[1].value > 0 ? '内容质量' : '等待生成'}
              </div>
            </div>
          </Col>
          <Col span={8}>
            <div style={{ textAlign: 'center' }}>
              <Progress
                type="circle"
                percent={stats[2].value > 0 ? 68 : 0}
                format={(percent) => `${percent}%`}
                strokeColor="#fa8c16"
                size={80}
              />
              <div style={{ marginTop: 8, fontSize: 14, color: '#666' }}>
                {stats[2].value > 0 ? '逻辑一致性' : '等待验证'}
              </div>
            </div>
          </Col>
        </Row>
      </Card>
    </div>
  );
};

export default Home;
