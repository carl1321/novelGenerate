import React, { useState } from 'react';
import { Card, Button, Input, message, Spin, Typography, Space } from 'antd';
import { CalendarOutlined, PlayCircleOutlined } from '@ant-design/icons';

const { Title, Paragraph } = Typography;
const { TextArea } = Input;

const Events: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [coreConcept, setCoreConcept] = useState('');
  const [result, setResult] = useState('');

  const handleGenerate = async () => {
    if (!coreConcept.trim()) {
      message.warning('请输入核心概念');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/generate/events', {
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
      setResult(data.result || '生成完成');
      message.success('事件生成成功！');
    } catch (error) {
      message.error(`生成失败: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <Title level={2}>
          <CalendarOutlined style={{ marginRight: 8 }} />
          5. 事件生成
        </Title>
        <Paragraph style={{ fontSize: 16, color: '#666' }}>
          根据核心概念生成具体的事件序列，为剧情发展提供丰富的事件内容。
        </Paragraph>
      </div>

      <Card style={{ marginBottom: 24 }}>
        <Title level={3}>输入核心概念</Title>
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <TextArea
            placeholder="请输入小说核心概念，例如：一个现代青年穿越到修仙世界，凭借现代知识在修仙界闯荡的故事"
            value={coreConcept}
            onChange={(e) => setCoreConcept(e.target.value)}
            rows={4}
          />
          <Button
            type="primary"
            size="large"
            loading={loading}
            onClick={handleGenerate}
            disabled={!coreConcept.trim()}
            icon={<PlayCircleOutlined />}
            style={{
              height: 50,
              fontSize: 16,
              fontWeight: 600,
            }}
          >
            {loading ? '正在生成...' : '开始生成事件'}
          </Button>
        </Space>
      </Card>

      {result && (
        <Card>
          <Title level={3}>生成结果</Title>
          <div style={{ 
            background: '#f5f5f5', 
            padding: 16, 
            borderRadius: 8,
            whiteSpace: 'pre-wrap',
            maxHeight: 500,
            overflow: 'auto'
          }}>
            <Spin spinning={loading}>
              {result}
            </Spin>
          </div>
        </Card>
      )}
    </div>
  );
};

export default Events;
