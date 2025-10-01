import React, { useState } from 'react';
import { Card, Button, Progress, List, Tag, Space, Statistic, Row, Col } from 'antd';
import { StarOutlined, TrophyOutlined, BarChartOutlined } from '@ant-design/icons';

const Scoring: React.FC = () => {
  const [scores, setScores] = useState({
    logicConsistency: 85,
    dramaticConflict: 78,
    characterConsistency: 92,
    writingQuality: 76,
    innovation: 68,
    total: 80,
  });

  const scoringItems = [
    {
      name: '逻辑自洽性',
      score: scores.logicConsistency,
      weight: 30,
      color: '#1890ff',
      description: '内容逻辑是否自洽，是否存在矛盾',
    },
    {
      name: '戏剧冲突性',
      score: scores.dramaticConflict,
      weight: 20,
      color: '#52c41a',
      description: '冲突是否激烈，是否有足够的张力',
    },
    {
      name: '角色一致性',
      score: scores.characterConsistency,
      weight: 20,
      color: '#fa8c16',
      description: '角色行为是否符合其设定',
    },
    {
      name: '文笔流畅度',
      score: scores.writingQuality,
      weight: 15,
      color: '#722ed1',
      description: '语言是否通顺优美',
    },
    {
      name: '创新性',
      score: scores.innovation,
      weight: 10,
      description: '是否脱离俗套，有创新点',
      color: '#eb2f96',
    },
  ];

  const getScoreLevel = (score: number) => {
    if (score >= 90) return { level: '优秀', color: '#52c41a' };
    if (score >= 80) return { level: '良好', color: '#1890ff' };
    if (score >= 70) return { level: '一般', color: '#faad14' };
    if (score >= 60) return { level: '较差', color: '#fa8c16' };
    return { level: '很差', color: '#ff4d4f' };
  };

  return (
    <div>
      <Card title="多维度评分系统" style={{ marginBottom: 16 }}>
        <Row gutter={16}>
          <Col span={6}>
            <Statistic
              title="总分"
              value={scores.total}
              suffix="分"
              valueStyle={{ color: '#1890ff', fontSize: 32 }}
              prefix={<TrophyOutlined />}
            />
          </Col>
          <Col span={6}>
            <Statistic
              title="评级"
              value={getScoreLevel(scores.total).level}
              valueStyle={{ 
                color: getScoreLevel(scores.total).color, 
                fontSize: 24 
              }}
            />
          </Col>
          <Col span={6}>
            <Statistic
              title="最高分项"
              value="角色一致性"
              valueStyle={{ color: '#52c41a' }}
            />
          </Col>
          <Col span={6}>
            <Statistic
              title="最低分项"
              value="创新性"
              valueStyle={{ color: '#ff4d4f' }}
            />
          </Col>
        </Row>
      </Card>

      <Card title="详细评分" extra={<Button icon={<BarChartOutlined />}>生成报告</Button>}>
        <List
          dataSource={scoringItems}
          renderItem={(item) => (
            <List.Item>
              <Card size="small" style={{ width: '100%' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', alignItems: 'center', marginBottom: 8 }}>
                      <StarOutlined style={{ color: item.color, marginRight: 8 }} />
                      <span style={{ fontWeight: 'bold', fontSize: 16 }}>{item.name}</span>
                      <Tag color={item.color} style={{ marginLeft: 8 }}>
                        权重 {item.weight}%
                      </Tag>
                    </div>
                    <div style={{ color: '#666', fontSize: 14 }}>{item.description}</div>
                  </div>
                  
                  <div style={{ width: 300, marginLeft: 16 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                      <span style={{ fontSize: 18, fontWeight: 'bold', color: item.color }}>
                        {item.score}分
                      </span>
                      <span style={{ color: '#666' }}>
                        {getScoreLevel(item.score).level}
                      </span>
                    </div>
                    <Progress 
                      percent={item.score} 
                      strokeColor={item.color}
                      showInfo={false}
                    />
                  </div>
                </div>
              </Card>
            </List.Item>
          )}
        />
      </Card>

      <Card title="评分建议" style={{ marginTop: 16 }}>
        <List
          dataSource={[
            '建议提升创新性，增加独特的情节设计',
            '文笔流畅度有待提高，可以增加更多细节描写',
            '戏剧冲突性可以进一步加强，增加更多转折',
            '角色一致性表现优秀，继续保持',
            '逻辑自洽性良好，注意细节的合理性',
          ]}
          renderItem={(item) => (
            <List.Item>
              <Space>
                <Tag color="blue">建议</Tag>
                {item}
              </Space>
            </List.Item>
          )}
        />
      </Card>
    </div>
  );
};

export default Scoring;
