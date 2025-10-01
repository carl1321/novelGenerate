import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Row, 
  Col, 
  Button, 
  Input, 
  Select, 
  Typography, 
  Space, 
  Divider,
  Alert,
  Spin,
  List,
  Modal,
  Form,
  message
} from 'antd';
import {
  GlobalOutlined,
  UserOutlined,
  BookOutlined,
  FileTextOutlined,
  CalendarOutlined,
  PlayCircleOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  ExclamationCircleOutlined,
} from '@ant-design/icons';

const { Title, Paragraph, Text } = Typography;
const { TextArea } = Input;
const { Option } = Select;

interface GenerationStep {
  id: string;
  name: string;
  description: string;
  icon: React.ReactNode;
  status: 'pending' | 'generating' | 'completed' | 'error';
  result?: any;
  error?: string;
}

const ManualGeneration: React.FC = () => {
  const [coreConcept, setCoreConcept] = useState('');
  const [generationSteps, setGenerationSteps] = useState<GenerationStep[]>([
    {
      id: 'worldview',
      name: '世界观生成',
      description: '生成修仙世界的世界观设定',
      icon: <GlobalOutlined />,
      status: 'pending'
    },
    {
      id: 'characters',
      name: '角色生成',
      description: '生成主要角色和正义伙伴',
      icon: <UserOutlined />,
      status: 'pending'
    },
    {
      id: 'plot_outline',
      name: '剧情大纲',
      description: '生成整体剧情大纲',
      icon: <BookOutlined />,
      status: 'pending'
    },
    {
      id: 'chapter_outline',
      name: '章节大纲',
      description: '生成章节详细大纲',
      icon: <FileTextOutlined />,
      status: 'pending'
    },
    {
      id: 'events',
      name: '事件生成',
      description: '生成具体事件序列',
      icon: <CalendarOutlined />,
      status: 'pending'
    },
    {
      id: 'detailed_plot',
      name: '详细剧情',
      description: '生成具体章节的详细剧情',
      icon: <PlayCircleOutlined />,
      status: 'pending'
    }
  ]);

  const [selectedChapter, setSelectedChapter] = useState<number | null>(null);
  const [selectedEvents, setSelectedEvents] = useState<string[]>([]);
  const [availableChapters, setAvailableChapters] = useState<any[]>([]);
  const [availableEvents, setAvailableEvents] = useState<any[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);

  // 组件加载时获取可用数据
  useEffect(() => {
    fetchChapters();
    fetchEvents();
  }, []);

  // 模拟API调用
  const callAPI = async (endpoint: string, data: any = {}) => {
    try {
      const response = await fetch(`http://localhost:8000/api/${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const result = await response.json();
      if (!result.success) {
        throw new Error(result.message || 'API调用失败');
      }
      
      return result.data;
    } catch (error) {
      console.error(`API call failed for ${endpoint}:`, error);
      throw error;
    }
  };

  const updateStepStatus = (stepId: string, status: GenerationStep['status'], result?: any, error?: string) => {
    setGenerationSteps(prev => 
      prev.map(step => 
        step.id === stepId 
          ? { ...step, status, result, error }
          : step
      )
    );
  };

  const generateWorldView = async () => {
    if (!coreConcept.trim()) {
      message.error('请输入核心概念');
      return;
    }

    updateStepStatus('worldview', 'generating');
    try {
      const response = await fetch('http://localhost:8000/api/v1/world/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          core_concept: coreConcept,
          description: '',
          additional_requirements: {}
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      updateStepStatus('worldview', 'completed', result);
      message.success('世界观生成完成');
    } catch (error) {
      updateStepStatus('worldview', 'error', undefined, error instanceof Error ? error.message : '生成失败');
      message.error('世界观生成失败');
    }
  };

  const generateCharacters = async () => {
    const worldviewStep = generationSteps.find(step => step.id === 'worldview');
    if (!worldviewStep || worldviewStep.status !== 'completed') {
      message.error('请先生成世界观');
      return;
    }

    updateStepStatus('characters', 'generating');
    try {
      const result = await callAPI('generate/characters', { 
        world_view: worldviewStep.result,
        core_concept: coreConcept 
      });
      updateStepStatus('characters', 'completed', result);
      message.success('角色生成完成');
    } catch (error) {
      updateStepStatus('characters', 'error', undefined, error instanceof Error ? error.message : '生成失败');
      message.error('角色生成失败');
    }
  };

  const generatePlotOutline = async () => {
    const worldviewStep = generationSteps.find(step => step.id === 'worldview');
    const charactersStep = generationSteps.find(step => step.id === 'characters');
    
    if (!worldviewStep || worldviewStep.status !== 'completed') {
      message.error('请先生成世界观');
      return;
    }
    if (!charactersStep || charactersStep.status !== 'completed') {
      message.error('请先生成角色');
      return;
    }

    updateStepStatus('plot_outline', 'generating');
    try {
      const result = await callAPI('generate/plot-outline', { 
        world_view: worldviewStep.result,
        characters: charactersStep.result,
        core_concept: coreConcept 
      });
      updateStepStatus('plot_outline', 'completed', result);
      message.success('剧情大纲生成完成');
    } catch (error) {
      updateStepStatus('plot_outline', 'error', undefined, error instanceof Error ? error.message : '生成失败');
      message.error('剧情大纲生成失败');
    }
  };

  const generateChapterOutline = async () => {
    const plotOutlineStep = generationSteps.find(step => step.id === 'plot_outline');
    if (!plotOutlineStep || plotOutlineStep.status !== 'completed') {
      message.error('请先生成剧情大纲');
      return;
    }

    updateStepStatus('chapter_outline', 'generating');
    try {
      const result = await callAPI('generate/chapter-outline', { 
        plot_outline: plotOutlineStep.result 
      });
      updateStepStatus('chapter_outline', 'completed', result);
      setAvailableChapters(result.chapters || []);
      message.success('章节大纲生成完成');
    } catch (error) {
      updateStepStatus('chapter_outline', 'error', undefined, error instanceof Error ? error.message : '生成失败');
      message.error('章节大纲生成失败');
    }
  };

  // 获取可用章节
  const fetchChapters = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/chapters');
      const result = await response.json();
      if (result.success) {
        setAvailableChapters(result.data);
      }
    } catch (error) {
      console.error('获取章节失败:', error);
    }
  };

  // 获取可用事件
  const fetchEvents = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/events');
      const result = await response.json();
      if (result.success) {
        setAvailableEvents(result.data);
      }
    } catch (error) {
      console.error('获取事件失败:', error);
    }
  };

  const generateEvents = async () => {
    const worldviewStep = generationSteps.find(step => step.id === 'worldview');
    const charactersStep = generationSteps.find(step => step.id === 'characters');
    const plotOutlineStep = generationSteps.find(step => step.id === 'plot_outline');
    
    if (!worldviewStep || worldviewStep.status !== 'completed') {
      message.error('请先生成世界观');
      return;
    }
    if (!charactersStep || charactersStep.status !== 'completed') {
      message.error('请先生成角色');
      return;
    }
    if (!plotOutlineStep || plotOutlineStep.status !== 'completed') {
      message.error('请先生成剧情大纲');
      return;
    }

    updateStepStatus('events', 'generating');
    try {
      const result = await callAPI('generate/events', { 
        world_view: worldviewStep.result,
        characters: charactersStep.result,
        plot_outline: plotOutlineStep.result,
        event_count: 20
      });
      updateStepStatus('events', 'completed', result);
      setAvailableEvents(result.events || []);
      message.success('事件生成完成');
    } catch (error) {
      updateStepStatus('events', 'error', undefined, error instanceof Error ? error.message : '生成失败');
      message.error('事件生成失败');
    }
  };

  const generateDetailedPlot = async () => {
    if (selectedChapter === null) {
      message.error('请选择要生成详细剧情的章节');
      return;
    }

    updateStepStatus('detailed_plot', 'generating');
    try {
      const result = await callAPI('generate/detailed-plot', { 
        chapter_index: selectedChapter,
        selected_events: selectedEvents.length > 0 ? selectedEvents : undefined
      });
      updateStepStatus('detailed_plot', 'completed', result);
      message.success('详细剧情生成完成');
    } catch (error) {
      updateStepStatus('detailed_plot', 'error', undefined, error instanceof Error ? error.message : '生成失败');
      message.error('详细剧情生成失败');
    }
  };

  const getStatusIcon = (status: GenerationStep['status']) => {
    switch (status) {
      case 'pending':
        return <ClockCircleOutlined style={{ color: '#d9d9d9' }} />;
      case 'generating':
        return <Spin size="small" />;
      case 'completed':
        return <CheckCircleOutlined style={{ color: '#52c41a' }} />;
      case 'error':
        return <ExclamationCircleOutlined style={{ color: '#ff4d4f' }} />;
    }
  };

  const getStatusColor = (status: GenerationStep['status']) => {
    switch (status) {
      case 'pending':
        return '#d9d9d9';
      case 'generating':
        return '#1890ff';
      case 'completed':
        return '#52c41a';
      case 'error':
        return '#ff4d4f';
    }
  };

  return (
    <div>
      <Title level={2}>手动生成控制台</Title>
      <Paragraph>
        您可以手动控制各个模块的生成过程，按照逻辑顺序逐步生成小说内容。
      </Paragraph>

      <Card style={{ marginBottom: 24 }}>
        <Title level={4}>核心概念设置</Title>
        <Space.Compact style={{ width: '100%' }}>
          <Input
            placeholder="请输入小说的核心概念，如：现代修仙者的都市生活"
            value={coreConcept}
            onChange={(e) => setCoreConcept(e.target.value)}
            style={{ flex: 1 }}
          />
          <Button type="primary" onClick={() => setCoreConcept('现代修仙者的都市生活')}>
            使用示例
          </Button>
        </Space.Compact>
      </Card>

      <Row gutter={[16, 16]}>
        {generationSteps.map((step, index) => (
          <Col xs={24} sm={12} lg={8} key={step.id}>
            <Card
              hoverable
              style={{ 
                height: '100%',
                border: `2px solid ${getStatusColor(step.status)}`,
                opacity: step.status === 'pending' ? 0.7 : 1
              }}
            >
              <div style={{ textAlign: 'center', marginBottom: 16 }}>
                <div style={{ fontSize: 32, marginBottom: 8 }}>
                  {step.icon}
                </div>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8 }}>
                  {getStatusIcon(step.status)}
                  <Text strong>{step.name}</Text>
                </div>
              </div>
              
              <Paragraph style={{ textAlign: 'center', color: '#666' }}>
                {step.description}
              </Paragraph>

              {step.status === 'error' && step.error && (
                <Alert
                  message="生成失败"
                  description={step.error}
                  type="error"
                  showIcon
                  style={{ marginBottom: 16 }}
                />
              )}

              {step.status === 'completed' && step.result && (
                <Alert
                  message="生成完成"
                  description={`已生成${step.result.count || 1}项内容`}
                  type="success"
                  showIcon
                  style={{ marginBottom: 16 }}
                />
              )}

              <Button
                type="primary"
                block
                loading={step.status === 'generating'}
                disabled={step.status === 'generating' || step.status === 'completed'}
                onClick={() => {
                  switch (step.id) {
                    case 'worldview':
                      generateWorldView();
                      break;
                    case 'characters':
                      generateCharacters();
                      break;
                    case 'plot_outline':
                      generatePlotOutline();
                      break;
                    case 'chapter_outline':
                      generateChapterOutline();
                      break;
                    case 'events':
                      generateEvents();
                      break;
                    case 'detailed_plot':
                      generateDetailedPlot();
                      break;
                  }
                }}
              >
                {step.status === 'generating' ? '生成中...' : 
                 step.status === 'completed' ? '重新生成' : 
                 '开始生成'}
              </Button>
            </Card>
          </Col>
        ))}
      </Row>

      {/* 详细剧情生成的特殊配置 */}
      <Card style={{ marginTop: 24 }}>
        <Title level={4}>详细剧情生成配置</Title>
        <Row gutter={16}>
          <Col span={12}>
            <div style={{ marginBottom: 16 }}>
              <Text strong>选择章节：</Text>
              <Select
                style={{ width: '100%', marginTop: 8 }}
                placeholder="请选择要生成详细剧情的章节"
                value={selectedChapter}
                onChange={setSelectedChapter}
                disabled={availableChapters.length === 0}
              >
                {availableChapters.map((chapter, index) => (
                  <Option key={index} value={index}>
                    第{index + 1}章: {chapter.title || `第${index + 1}章`}
                  </Option>
                ))}
              </Select>
            </div>
          </Col>
          <Col span={12}>
            <div style={{ marginBottom: 16 }}>
              <Text strong>选择事件：</Text>
              <Select
                mode="multiple"
                style={{ width: '100%', marginTop: 8 }}
                placeholder="选择要包含的事件（可选）"
                value={selectedEvents}
                onChange={setSelectedEvents}
                disabled={availableEvents.length === 0}
              >
                {availableEvents.map((event, index) => (
                  <Option key={event.id || index} value={event.id || index}>
                    {event.title || `事件${index + 1}`}
                  </Option>
                ))}
              </Select>
            </div>
          </Col>
        </Row>
      </Card>

      {/* 生成进度总览 */}
      <Card style={{ marginTop: 24 }}>
        <Title level={4}>生成进度总览</Title>
        <Row gutter={16}>
          <Col span={6}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 24, fontWeight: 'bold', color: '#1890ff' }}>
                {generationSteps.filter(step => step.status === 'completed').length}
              </div>
              <div>已完成</div>
            </div>
          </Col>
          <Col span={6}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 24, fontWeight: 'bold', color: '#52c41a' }}>
                {generationSteps.filter(step => step.status === 'generating').length}
              </div>
              <div>生成中</div>
            </div>
          </Col>
          <Col span={6}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 24, fontWeight: 'bold', color: '#d9d9d9' }}>
                {generationSteps.filter(step => step.status === 'pending').length}
              </div>
              <div>待生成</div>
            </div>
          </Col>
          <Col span={6}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 24, fontWeight: 'bold', color: '#ff4d4f' }}>
                {generationSteps.filter(step => step.status === 'error').length}
              </div>
              <div>生成失败</div>
            </div>
          </Col>
        </Row>
      </Card>
    </div>
  );
};

export default ManualGeneration;
