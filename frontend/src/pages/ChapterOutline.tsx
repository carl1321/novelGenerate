import React, { useState } from 'react';
import { Card, Button, Input, message, Spin, Typography, Space } from 'antd';
import { BulbOutlined, PlayCircleOutlined } from '@ant-design/icons';

const { Title, Paragraph } = Typography;
const { TextArea } = Input;

const ChapterOutline: React.FC = () => {
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
      const response = await fetch('http://localhost:8000/api/generate/chapter-outline', {
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
      message.success('章节大纲生成成功！');
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
          <BulbOutlined style={{ marginRight: 8 }} />
          4. 章节大纲生成
        </Title>
        <Paragraph style={{ fontSize: 16, color: '#666' }}>
          根据核心概念生成详细的章节大纲，规划每个章节的具体内容。
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
            {loading ? '正在生成...' : '开始生成章节大纲'}
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

export default ChapterOutline;
