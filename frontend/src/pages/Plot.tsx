import React, { useState } from 'react';
import { Card, Button, List, Tag, Space, Timeline, Progress, Input, message } from 'antd';
import { BookOutlined, PlusOutlined, PlayCircleOutlined } from '@ant-design/icons';

const Plot: React.FC = () => {
  const [coreConcept, setCoreConcept] = useState('');
  const [loading, setLoading] = useState(false);
  const [plotNodes, setPlotNodes] = useState([
    {
      id: 1,
      title: '初入修炼',
      description: '主角踏上修炼之路',
      type: '主线',
      status: '已完成',
      progress: 100,
    },
    {
      id: 2,
      title: '宗门大比',
      description: '参加宗门大比，展现实力',
      type: '主线',
      status: '进行中',
      progress: 60,
    },
    {
      id: 3,
      title: '秘境探险',
      description: '探索神秘秘境，获得机缘',
      type: '支线',
      status: '未开始',
      progress: 0,
    },
  ]);

  const handleGeneratePlot = async () => {
    if (!coreConcept.trim()) {
      message.warning('请输入核心概念');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/generate/plot-outline', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ core_concept: coreConcept }),
        signal: AbortSignal.timeout(600000), // 600秒超时
      });

      if (!response.ok) {
        throw new Error('生成失败');
      }

      const data = await response.json();
      message.success('剧情大纲生成成功！');
      setCoreConcept('');
      
      // 可以在这里更新剧情节点列表
      // setPlotNodes(prev => [...prev, data.result]);
    } catch (error) {
      message.error(`生成失败: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <Card 
        title="3. 剧情大纲生成" 
        extra={
          <Space>
            <Input
              placeholder="请输入核心概念"
              value={coreConcept}
              onChange={(e) => setCoreConcept(e.target.value)}
              style={{ width: 200 }}
            />
            <Button 
              type="primary" 
              icon={<PlayCircleOutlined />}
              loading={loading}
              onClick={handleGeneratePlot}
              disabled={!coreConcept.trim()}
            >
              生成剧情大纲
            </Button>
          </Space>
        }
      >
        <Timeline>
          {plotNodes.map((node) => (
            <Timeline.Item
              key={node.id}
              color={node.status === '已完成' ? 'green' : node.status === '进行中' ? 'blue' : 'gray'}
            >
              <Card size="small" style={{ marginBottom: 16 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <h4 style={{ margin: 0 }}>
                      <BookOutlined style={{ marginRight: 8 }} />
                      {node.title}
                    </h4>
                    <p style={{ margin: '8px 0', color: '#666' }}>{node.description}</p>
                    <Space>
                      <Tag color={node.type === '主线' ? 'blue' : 'green'}>{node.type}</Tag>
                      <Tag color={node.status === '已完成' ? 'green' : node.status === '进行中' ? 'blue' : 'default'}>
                        {node.status}
                      </Tag>
                    </Space>
                  </div>
                  <div style={{ width: 200 }}>
                    <Progress percent={node.progress} size="small" />
                  </div>
                </div>
              </Card>
            </Timeline.Item>
          ))}
        </Timeline>
      </Card>

      <Card title="剧情统计" style={{ marginTop: 16 }}>
        <div style={{ display: 'flex', justifyContent: 'space-around' }}>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: 24, fontWeight: 'bold', color: '#1890ff' }}>12</div>
            <div>总剧情节点</div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: 24, fontWeight: 'bold', color: '#52c41a' }}>8</div>
            <div>已完成</div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: 24, fontWeight: 'bold', color: '#fa8c16' }}>3</div>
            <div>进行中</div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: 24, fontWeight: 'bold', color: '#666' }}>1</div>
            <div>未开始</div>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default Plot;
