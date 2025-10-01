import React, { useState } from 'react';
import { Card, Button, List, Tag, Space, Steps, Alert, Progress } from 'antd';
import { SyncOutlined, BulbOutlined, ExperimentOutlined, CheckCircleOutlined } from '@ant-design/icons';

const { Step } = Steps;

const Evolution: React.FC = () => {
  const [currentStep, setCurrentStep] = useState(0);
  const [evolutionTasks, setEvolutionTasks] = useState([
    {
      id: 1,
      title: '问题定位',
      status: 'completed',
      description: '识别内容中的逻辑问题和改进点',
      issues: ['角色行为不一致', '情节发展过快'],
    },
    {
      id: 2,
      title: '重写建议生成',
      status: 'in_progress',
      description: '基于问题分析生成具体的修改建议',
      suggestions: ['调整角色对话风格', '增加过渡情节'],
    },
    {
      id: 3,
      title: 'A/B测试版本',
      status: 'pending',
      description: '生成多个版本进行对比测试',
      versions: ['保守版本', '激进版本', '创新版本'],
    },
    {
      id: 4,
      title: '迭代优化',
      status: 'pending',
      description: '根据测试结果进行最终优化',
      optimizations: [],
    },
  ]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'success';
      case 'in_progress': return 'processing';
      case 'pending': return 'default';
      default: return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircleOutlined style={{ color: '#52c41a' }} />;
      case 'in_progress': return <SyncOutlined spin style={{ color: '#1890ff' }} />;
      case 'pending': return <BulbOutlined style={{ color: '#d9d9d9' }} />;
      default: return null;
    }
  };

  return (
    <div>
      <Card title="进化与重写引擎" style={{ marginBottom: 16 }}>
        <Alert
          message="进化引擎正在运行"
          description="系统正在分析内容问题并生成改进方案，预计需要2-3分钟完成。"
          type="info"
          showIcon
          style={{ marginBottom: 16 }}
        />
        
        <Steps current={currentStep} style={{ marginBottom: 24 }}>
          <Step title="问题定位" icon={<BulbOutlined />} />
          <Step title="重写建议" icon={<SyncOutlined />} />
          <Step title="A/B测试" icon={<ExperimentOutlined />} />
          <Step title="迭代优化" icon={<CheckCircleOutlined />} />
        </Steps>
        
        <Space style={{ marginBottom: 16 }}>
          <Button type="primary" icon={<SyncOutlined />}>
            开始进化
          </Button>
          <Button>暂停进程</Button>
          <Button>查看详情</Button>
        </Space>
      </Card>

      <Card title="进化任务">
        <List
          dataSource={evolutionTasks}
          renderItem={(item) => (
            <List.Item>
              <Card size="small" style={{ width: '100%' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', alignItems: 'center', marginBottom: 8 }}>
                      {getStatusIcon(item.status)}
                      <span style={{ marginLeft: 8, fontWeight: 'bold', fontSize: 16 }}>
                        {item.title}
                      </span>
                      <Tag color={getStatusColor(item.status)} style={{ marginLeft: 8 }}>
                        {item.status === 'completed' ? '已完成' : 
                         item.status === 'in_progress' ? '进行中' : '待处理'}
                      </Tag>
                    </div>
                    
                    <div style={{ color: '#666', marginBottom: 8 }}>{item.description}</div>
                    
                    {item.issues && item.issues.length > 0 && (
                      <div style={{ marginBottom: 8 }}>
                        <div style={{ color: '#666', marginBottom: 4 }}>发现的问题：</div>
                        <Space wrap>
                          {item.issues.map((issue, index) => (
                            <Tag key={index} color="red">{issue}</Tag>
                          ))}
                        </Space>
                      </div>
                    )}
                    
                    {item.suggestions && item.suggestions.length > 0 && (
                      <div style={{ marginBottom: 8 }}>
                        <div style={{ color: '#666', marginBottom: 4 }}>修改建议：</div>
                        <Space wrap>
                          {item.suggestions.map((suggestion, index) => (
                            <Tag key={index} color="blue">{suggestion}</Tag>
                          ))}
                        </Space>
                      </div>
                    )}
                    
                    {item.versions && item.versions.length > 0 && (
                      <div>
                        <div style={{ color: '#666', marginBottom: 4 }}>测试版本：</div>
                        <Space wrap>
                          {item.versions.map((version, index) => (
                            <Tag key={index} color="green">{version}</Tag>
                          ))}
                        </Space>
                      </div>
                    )}
                  </div>
                  
                  <div style={{ width: 200, marginLeft: 16 }}>
                    <Progress 
                      percent={item.status === 'completed' ? 100 : 
                              item.status === 'in_progress' ? 60 : 0} 
                      size="small"
                      strokeColor={item.status === 'completed' ? '#52c41a' : '#1890ff'}
                    />
                  </div>
                </div>
              </Card>
            </List.Item>
          )}
        />
      </Card>

      <Card title="进化统计" style={{ marginTop: 16 }}>
        <div style={{ display: 'flex', justifyContent: 'space-around' }}>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: 24, fontWeight: 'bold', color: '#1890ff' }}>4</div>
            <div>总任务数</div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: 24, fontWeight: 'bold', color: '#52c41a' }}>1</div>
            <div>已完成</div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: 24, fontWeight: 'bold', color: '#faad14' }}>1</div>
            <div>进行中</div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: 24, fontWeight: 'bold', color: '#666' }}>2</div>
            <div>待处理</div>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default Evolution;
