import React, { useState, useEffect } from 'react';
import { 
  Card, Button, Input, message, Spin, Typography, Space, 
  Tabs, Timeline, Progress, Tag, Row, Col, Statistic,
  Modal, Form, Select, InputNumber, Divider, Tooltip
} from 'antd';
import { 
  BookOutlined, PlayCircleOutlined, EyeOutlined, EditOutlined,
  BarChartOutlined, NodeIndexOutlined, HeartOutlined, 
  ThunderboltOutlined, CrownOutlined, SettingOutlined, DeleteOutlined,
  PlusOutlined
} from '@ant-design/icons';

const { Title, Paragraph, Text } = Typography;
const { TextArea } = Input;
const { Option } = Select;

interface PlotOutline {
  id: string;
  title: string;
  worldview_id: string;
  
  // 故事核心信息
  story_summary: string;
  core_conflict: string;
  story_tone: string;
  narrative_structure: string;
  theme: string;
  
  // 主角信息
  protagonist_name: string;
  protagonist_background: string;
  protagonist_personality: string;
  protagonist_goals: string;
  
  // 世界观信息
  core_concept: string;
  world_description: string;
  geography_setting: string;
  
  // 幕次结构
  acts: Array<{
    act_number: number;
    act_name: string;
    core_mission: string;
    daily_events: string;
    conflict_events: string;
    special_events: string;
    major_events: string;
    stage_result: string;
  }>;
  
  // 技术参数
  target_word_count: number;
  estimated_chapters: number;
  
  // 状态信息
  status: string;
  created_at: string;
  updated_at: string;
  created_by: string;
}

interface WorldView {
  worldview_id: string;
  name: string;
  description: string;
  core_concept: string;
  created_at: string;
  updated_at: string;
  created_by: string;
  version: number;
  status: string;
}

// 角色精简信息（用于下拉选择）
interface CharacterSummary {
  id: string;
  name: string;
  role_type: string;
}

const PlotOutline: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [plotOutline, setPlotOutline] = useState<PlotOutline | null>(null);
  const [plotOutlines, setPlotOutlines] = useState<PlotOutline[]>([]);
  const [worldViews, setWorldViews] = useState<WorldView[]>([]);
  const [characters, setCharacters] = useState<CharacterSummary[]>([]);
  const [showGenerateModal, setShowGenerateModal] = useState(false);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [showPlotList, setShowPlotList] = useState(true);
  const [form] = Form.useForm();

  // 获取世界观列表
  const fetchWorldViews = async () => {
    try {
      console.log('正在获取世界观列表...');
      const response = await fetch('/api/v1/world/list');
      if (!response.ok) {
        throw new Error(`获取世界观列表失败: ${response.status} ${response.statusText}`);
      }
      const data = await response.json();
      console.log('获取到世界观列表:', data);
      // 处理不同的数据格式
      if (Array.isArray(data)) {
        setWorldViews(data);
      } else if (data.worldviews && Array.isArray(data.worldviews)) {
        setWorldViews(data.worldviews);
      } else {
        setWorldViews([]);
      }
    } catch (error) {
      console.error('获取世界观列表失败:', error);
      message.error(`获取世界观列表失败: ${error.message}`);
    }
  };

  // 获取角色列表（用于主角选择）
  const fetchCharacters = async () => {
    try {
      console.log('正在获取角色列表...');
      const response = await fetch('/api/v1/character/list');
      if (!response.ok) {
        throw new Error(`获取角色列表失败: ${response.status} ${response.statusText}`);
      }
      const data = await response.json();
      console.log('获取到角色列表:', data);
      // 适配后端返回结构
      if (Array.isArray(data)) {
        setCharacters(data as CharacterSummary[]);
      } else if (data.characters && Array.isArray(data.characters)) {
        setCharacters(data.characters as CharacterSummary[]);
      } else {
        console.log('角色数据格式不正确:', data);
        setCharacters([]);
      }
    } catch (error: any) {
      console.error('获取角色列表失败:', error);
      message.error(`获取角色列表失败: ${error.message}`);
      setCharacters([]);
    }
  };

  // 处理剧情大纲更新
  const handlePlotUpdate = (updatedPlot: PlotOutline) => {
    setPlotOutline(updatedPlot);
    setPlotOutlines(prev => prev.map(plot => 
      plot.id === updatedPlot.id ? updatedPlot : plot
    ));
  };

  // 获取剧情大纲列表
  const fetchPlotOutlines = async () => {
    setLoading(true);
    try {
      console.log('正在获取剧情大纲列表...');
      const response = await fetch('/api/v1/plot/plot-outlines');
      if (!response.ok) {
        throw new Error(`获取列表失败: ${response.status} ${response.statusText}`);
      }
      const data = await response.json();
      console.log('获取到剧情大纲列表:', data);
      setPlotOutlines(data);
    } catch (error) {
      console.error('获取列表失败:', error);
      message.error(`获取列表失败: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  // 获取单个剧情大纲详情
  const fetchPlotOutline = async (plotId: string) => {
    setLoading(true);
    try {
      console.log('正在获取剧情大纲详情:', plotId);
      const response = await fetch(`/api/v1/plot/plot-outlines/${plotId}`);
      if (!response.ok) {
        throw new Error(`获取详情失败: ${response.status} ${response.statusText}`);
      }
      const data = await response.json();
      console.log('获取到剧情大纲数据:', data);
      setPlotOutline(data);
      setShowDetailModal(true);
      message.success('剧情大纲详情加载成功！');
    } catch (error) {
      console.error('获取详情失败:', error);
      message.error(`获取详情失败: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  // 删除剧情大纲
  const deletePlotOutline = async (plotId: string) => {
    try {
      const response = await fetch(`/api/v1/plot/plot-outlines/${plotId}`, {
        method: 'DELETE',
      });
      if (!response.ok) {
        throw new Error('删除失败');
      }
      message.success('剧情大纲删除成功！');
      // 刷新列表
      fetchPlotOutlines();
    } catch (error) {
      message.error(`删除失败: ${error.message}`);
    }
  };

  // 组件加载时获取列表
  useEffect(() => {
    fetchPlotOutlines();
    fetchWorldViews();
    fetchCharacters();
  }, []);

  // 生成剧情大纲
  const handleGeneratePlot = async (values: any) => {
    setLoading(true);
    try {
      if (!values.worldview_id) {
        message.error('请选择世界观');
        setLoading(false);
        return;
      }

      const response = await fetch('/api/v1/plot/plot-outlines/simple', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          worldview_id: values.worldview_id,
          title: values.title,
          core_conflict: values.core_conflict,
          story_tone: values.tone || "热血",
          narrative_structure: values.narrative_structure || "线性叙事",
          story_structure: values.story_structure || "5幕式",
          theme: values.theme || "成长与正义",
          protagonist_character_id: values.protagonist_character_id,
          target_word_count: values.target_word_count || 100000,
          estimated_chapters: values.estimated_chapters || 20
        }),
        signal: AbortSignal.timeout(600000),
      });

      if (!response.ok) {
        throw new Error('生成失败');
      }

      const data = await response.json();
      if (data.success) {
        setPlotOutline(data.plot_outline);
        message.success('剧情大纲生成成功！');
        setShowGenerateModal(false);
        setShowDetailModal(true);
        form.resetFields();
        // 刷新列表
        fetchPlotOutlines();
      } else {
        throw new Error(data.message);
      }
    } catch (error) {
      message.error(`生成失败: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  // 故事框架可视化组件
  const StoryFrameworkVisualization = ({ plotOutline }: { plotOutline: PlotOutline }) => (
    <Card title="故事框架" extra={<BarChartOutlined />}>
      <Row gutter={[16, 16]}>
        {/* 故事简介 */}
        <Col span={24}>
          <Title level={4}>故事简介</Title>
          <Paragraph>{plotOutline.story_summary}</Paragraph>
        </Col>
        
        {/* 故事要素 */}
        <Col span={24}>
          <Title level={4}>故事要素</Title>
          <Row gutter={16}>
            <Col span={12}>
              <Card size="small">
                <Text strong>核心冲突：</Text>
                <Text>{plotOutline.core_conflict}</Text>
              </Card>
            </Col>
            <Col span={12}>
              <Card size="small">
                <Text strong>故事基调：</Text>
                <Tag color="blue">{plotOutline.story_tone}</Tag>
              </Card>
            </Col>
          </Row>
          <Row gutter={16} style={{ marginTop: 8 }}>
            <Col span={12}>
              <Card size="small">
                <Text strong>叙事结构：</Text>
                <Tag color="green">{plotOutline.narrative_structure}</Tag>
              </Card>
            </Col>
            <Col span={12}>
              <Card size="small">
                <Text strong>主题思想：</Text>
                <Text>{plotOutline.theme}</Text>
              </Card>
            </Col>
          </Row>
        </Col>
        
        
        {/* 幕次结构 */}
        <Col span={24}>
          <Title level={4}>幕次结构</Title>
          <Timeline>
            {(plotOutline.acts || []).map((act, index) => (
              <Timeline.Item
                key={act.act_number}
                color={index === 0 ? 'green' : index === 1 ? 'blue' : 'red'}
              >
                <Card size="small">
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div style={{ flex: 1 }}>
                      <Title level={5} style={{ margin: 0 }}>
                        第{act.act_number}幕：{act.act_name}
                      </Title>
                      
                      <div style={{ marginTop: 8 }}>
                        <Text strong style={{ color: '#1890ff' }}>核心任务：</Text>
                        <Text>{act.core_mission}</Text>
                      </div>
                      
                      <div style={{ marginTop: 4 }}>
                        <Text strong style={{ color: '#52c41a' }}>日常事件：</Text>
                        <Text>{act.daily_events}</Text>
                      </div>
                      
                      <div style={{ marginTop: 4 }}>
                        <Text strong style={{ color: '#fa541c' }}>冲突事件：</Text>
                        <Text>{act.conflict_events}</Text>
                      </div>
                      
                      <div style={{ marginTop: 4 }}>
                        <Text strong style={{ color: '#722ed1' }}>特殊事件：</Text>
                        <Text>{act.special_events}</Text>
                      </div>
                      
                      <div style={{ marginTop: 4 }}>
                        <Text strong style={{ color: '#eb2f96' }}>重大事件：</Text>
                        <Text>{act.major_events}</Text>
                      </div>
                      
                      <div style={{ marginTop: 4 }}>
                        <Text strong style={{ color: '#13c2c2' }}>阶段结果：</Text>
                        <Text>{act.stage_result}</Text>
                      </div>
                    </div>
                  </div>
                </Card>
              </Timeline.Item>
            ))}
          </Timeline>
        </Col>

      </Row>
    </Card>
  );

  // 剧情大纲编辑表单组件
  const PlotOutlineEditForm = ({ plotOutline, onUpdate }: { plotOutline: PlotOutline, onUpdate: (updatedPlot: PlotOutline) => void }) => {
    const [form] = Form.useForm();
    const [loading, setLoading] = useState(false);

    useEffect(() => {
      form.setFieldsValue({
        title: plotOutline.title,
        story_summary: plotOutline.story_summary,
        core_conflict: plotOutline.core_conflict,
        story_tone: plotOutline.story_tone,
        narrative_structure: plotOutline.narrative_structure,
        theme: plotOutline.theme,
        target_word_count: plotOutline.target_word_count,
        estimated_chapters: plotOutline.estimated_chapters,
        acts: plotOutline.acts
      });
    }, [plotOutline, form]);

    const handleSubmit = async (values: any) => {
      setLoading(true);
      try {
        const updatedPlot = {
          ...plotOutline,
          ...values,
          updated_at: new Date().toISOString()
        };
        
        const response = await fetch(`/api/v1/plot/plot-outlines/${plotOutline.id}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(updatedPlot),
        });

        if (!response.ok) {
          throw new Error('更新失败');
        }

        message.success('剧情大纲更新成功！');
        onUpdate(updatedPlot);
      } catch (error: any) {
        message.error(`更新失败: ${error.message}`);
      } finally {
        setLoading(false);
      }
    };

    return (
      <Form form={form} layout="vertical" onFinish={handleSubmit}>
        <Row gutter={16}>
          <Col span={12}>
            <Form.Item
              name="title"
              label="小说标题"
              rules={[{ required: true, message: '请输入小说标题' }]}
            >
              <Input />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item
              name="story_tone"
              label="故事基调"
              rules={[{ required: true, message: '请选择故事基调' }]}
            >
              <Select>
                <Option value="热血">热血</Option>
                <Option value="轻松">轻松</Option>
                <Option value="悬疑">悬疑</Option>
                <Option value="浪漫">浪漫</Option>
                <Option value="黑暗">黑暗</Option>
              </Select>
            </Form.Item>
          </Col>
        </Row>

        <Form.Item
          name="story_summary"
          label="故事简介"
          rules={[{ required: true, message: '请输入故事简介' }]}
        >
          <TextArea rows={4} />
        </Form.Item>

        <Form.Item
          name="core_conflict"
          label="核心冲突"
          rules={[{ required: true, message: '请输入核心冲突' }]}
        >
          <TextArea rows={3} />
        </Form.Item>

        <Row gutter={16}>
          <Col span={12}>
            <Form.Item
              name="narrative_structure"
              label="叙事结构"
              rules={[{ required: true, message: '请选择叙事结构' }]}
            >
              <Select>
                <Option value="线性叙事">线性叙事</Option>
                <Option value="非线性叙事">非线性叙事</Option>
                <Option value="多视角叙事">多视角叙事</Option>
              </Select>
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item
              name="theme"
              label="主题思想"
              rules={[{ required: true, message: '请输入主题思想' }]}
            >
              <Input />
            </Form.Item>
          </Col>
        </Row>

        <Row gutter={16}>
          <Col span={12}>
            <Form.Item
              name="target_word_count"
              label="目标字数"
              rules={[{ required: true, message: '请输入目标字数' }]}
            >
              <InputNumber
                style={{ width: '100%' }}
                min={10000}
                max={1000000}
                step={10000}
              />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item
              name="estimated_chapters"
              label="预估章节数"
              rules={[{ required: true, message: '请输入预估章节数' }]}
            >
              <InputNumber
                style={{ width: '100%' }}
                min={5}
                max={200}
                step={5}
              />
            </Form.Item>
          </Col>
        </Row>

        <Form.List name="acts">
          {(fields, { add, remove }) => (
            <>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
                <Title level={4} style={{ margin: 0 }}>幕次结构</Title>
                <Button type="dashed" onClick={() => add()} icon={<PlusOutlined />}>
                  添加幕次
                </Button>
              </div>
              {fields.map(({ key, name, ...restField }) => (
                <Card key={key} size="small" style={{ marginBottom: 16 }}>
                  <Row gutter={16}>
                    <Col span={12}>
                      <Form.Item
                        {...restField}
                        name={[name, 'act_number']}
                        label="幕次编号"
                        rules={[{ required: true, message: '请输入幕次编号' }]}
                      >
                        <InputNumber min={1} max={20} style={{ width: '100%' }} />
                      </Form.Item>
                    </Col>
                    <Col span={12}>
                      <Form.Item
                        {...restField}
                        name={[name, 'act_name']}
                        label="幕次名称"
                        rules={[{ required: true, message: '请输入幕次名称' }]}
                      >
                        <Input />
                      </Form.Item>
                    </Col>
                  </Row>
                  
                  <Form.Item
                    {...restField}
                    name={[name, 'core_mission']}
                    label="核心任务"
                    rules={[{ required: true, message: '请输入核心任务' }]}
                  >
                    <TextArea rows={2} />
                  </Form.Item>

                  <Row gutter={16}>
                    <Col span={12}>
                      <Form.Item
                        {...restField}
                        name={[name, 'daily_events']}
                        label="日常事件"
                        rules={[{ required: true, message: '请输入日常事件' }]}
                      >
                        <TextArea rows={2} />
                      </Form.Item>
                    </Col>
                    <Col span={12}>
                      <Form.Item
                        {...restField}
                        name={[name, 'conflict_events']}
                        label="冲突事件"
                        rules={[{ required: true, message: '请输入冲突事件' }]}
                      >
                        <TextArea rows={2} />
                      </Form.Item>
                    </Col>
                  </Row>

                  <Row gutter={16}>
                    <Col span={12}>
                      <Form.Item
                        {...restField}
                        name={[name, 'special_events']}
                        label="特殊事件"
                        rules={[{ required: true, message: '请输入特殊事件' }]}
                      >
                        <TextArea rows={2} />
                      </Form.Item>
                    </Col>
                    <Col span={12}>
                      <Form.Item
                        {...restField}
                        name={[name, 'major_events']}
                        label="重大事件"
                        rules={[{ required: true, message: '请输入重大事件' }]}
                      >
                        <TextArea rows={2} />
                      </Form.Item>
                    </Col>
                  </Row>

                  <Form.Item
                    {...restField}
                    name={[name, 'stage_result']}
                    label="阶段结果"
                    rules={[{ required: true, message: '请输入阶段结果' }]}
                  >
                    <TextArea rows={2} />
                  </Form.Item>

                  <div style={{ textAlign: 'right' }}>
                    <Button type="link" danger onClick={() => remove(name)}>
                      删除幕次
                    </Button>
                  </div>
                </Card>
              ))}
            </>
          )}
        </Form.List>

        <Form.Item>
          <Button type="primary" htmlType="submit" loading={loading} size="large">
            保存更新
          </Button>
        </Form.Item>
      </Form>
    );
  };


  // 角色定位组件
  const CharacterPositionsCard = ({ positions }: { positions: any }) => (
    <Card title="角色定位" extra={<CrownOutlined />}>
      <div>此功能已移除</div>
    </Card>
  );

  // 核心剧情块组件
  const PlotBlocksCard = ({ blocks }: { blocks: any }) => (
    <Card title="核心剧情块" extra={<NodeIndexOutlined />}>
      <div>此功能已移除</div>
    </Card>
  );

  // 故事脉络组件
  const StoryFlowCard = ({ flow }: { flow: any }) => (
    <Card title="故事脉络" extra={<HeartOutlined />}>
      <div>此功能已移除</div>
    </Card>
  );


  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <Title level={2}>
          <BookOutlined style={{ marginRight: 8 }} />
          剧情大纲设计
        </Title>
        <Paragraph style={{ fontSize: 16, color: '#666' }}>
          设计完整的故事框架，包括故事结构、核心冲突、故事弧线和关键情节点。
        </Paragraph>
      </div>

      {/* 生成按钮 */}
      <Card style={{ marginBottom: 24 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <Title level={3} style={{ margin: 0 }}>创建新的剧情大纲</Title>
            <Text type="secondary">设计完整的故事框架和脉络</Text>
          </div>
          <Button
            type="primary"
            size="large"
            icon={<PlayCircleOutlined />}
            onClick={() => setShowGenerateModal(true)}
            style={{ height: 50, fontSize: 16 }}
          >
            生成剧情大纲
          </Button>
        </div>
      </Card>

      {/* 剧情大纲列表 */}
      {showPlotList && (
        <Card title="剧情大纲列表" style={{ marginBottom: 24 }}>
          <Spin spinning={loading}>
            {plotOutlines.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '40px 0' }}>
                <Text type="secondary">暂无剧情大纲，点击上方按钮创建新的剧情大纲</Text>
              </div>
            ) : (
              <Row gutter={[16, 16]}>
                {plotOutlines.map((plot) => (
                  <Col span={24} key={plot.id}>
                    <Card
                      hoverable
                      actions={[
                        <Button
                          key="view"
                          type="link"
                          icon={<EyeOutlined />}
                          onClick={() => fetchPlotOutline(plot.id)}
                        >
                          查看详情
                        </Button>,
                        <Button
                          key="edit"
                          type="link"
                          icon={<EditOutlined />}
                          onClick={() => {
                            setPlotOutline(plot);
                            setShowDetailModal(true);
                          }}
                        >
                          编辑
                        </Button>,
                        <Button
                          key="delete"
                          type="link"
                          danger
                          icon={<DeleteOutlined />}
                          onClick={() => {
                            Modal.confirm({
                              title: '确认删除',
                              content: `确定要删除剧情大纲"${plot.title}"吗？此操作不可撤销。`,
                              okText: '删除',
                              okType: 'danger',
                              cancelText: '取消',
                              onOk: () => deletePlotOutline(plot.id),
                            });
                          }}
                        >
                          删除
                        </Button>
                      ]}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                        <div style={{ flex: 1 }}>
                          <Title level={4} style={{ margin: 0, marginBottom: 8 }}>
                            {plot.title}
                          </Title>
                          <Paragraph 
                            ellipsis={{ rows: 2, expandable: false }}
                            style={{ marginBottom: 12 }}
                          >
                            {plot.story_summary}
                          </Paragraph>
                          <Space wrap>
                            <Tag color="green">{plot.story_tone}</Tag>
                            <Tag color="orange">{plot.narrative_structure}</Tag>
                            <Tag color="purple">{plot.status}</Tag>
                          </Space>
                        </div>
                        <div style={{ width: 200, textAlign: 'right' }}>
                          <Statistic
                            title="目标字数"
                            value={plot.target_word_count}
                            suffix="字"
                            valueStyle={{ fontSize: '16px' }}
                          />
                          <Statistic
                            title="预估章节"
                            value={plot.estimated_chapters}
                            suffix="章"
                            valueStyle={{ fontSize: '16px' }}
                          />
                          <Text type="secondary" style={{ fontSize: '12px' }}>
                            {plot.created_at ? new Date(plot.created_at).toLocaleDateString() : ''}
                          </Text>
                        </div>
                      </div>
                    </Card>
                  </Col>
                ))}
              </Row>
            )}
          </Spin>
        </Card>
      )}

      {/* 剧情大纲详情模态框 */}
      <Modal
        title="剧情大纲详情"
        open={showDetailModal}
        onCancel={() => {
          setShowDetailModal(false);
          setPlotOutline(null);
        }}
        footer={null}
        width="90%"
        style={{ top: 20 }}
        bodyStyle={{ maxHeight: '80vh', overflowY: 'auto' }}
      >
        {plotOutline && (
          <div>
            {/* 基本信息 */}
            <Card style={{ marginBottom: 24 }}>
              <Row gutter={[16, 16]}>
                <Col span={12}>
                  <Title level={3} style={{ margin: 0 }}>{plotOutline.title}</Title>
                  <Paragraph>{plotOutline.story_summary}</Paragraph>
                </Col>
                <Col span={12}>
                  <Row gutter={[16, 16]}>
                    <Col span={12}>
                      <Statistic title="目标字数" value={plotOutline.target_word_count} suffix="字" />
                    </Col>
                    <Col span={12}>
                      <Statistic title="预估章节" value={plotOutline.estimated_chapters} suffix="章" />
                    </Col>
                    <Col span={12}>
                      <Text strong>故事基调：</Text>
                      <Tag color="orange">{plotOutline.story_tone}</Tag>
                    </Col>
                    <Col span={12}>
                      <Text strong>叙事结构：</Text>
                      <Tag color="blue">{plotOutline.narrative_structure}</Tag>
                    </Col>
                    <Col span={12}>
                      <Text strong>世界观ID：</Text>
                      <Tag color="purple">{plotOutline.worldview_id}</Tag>
                    </Col>
                  </Row>
                </Col>
              </Row>
            </Card>

            {/* 详细内容 */}
            <Tabs defaultActiveKey="framework" type="card">
              <Tabs.TabPane tab="故事框架" key="framework">
                <StoryFrameworkVisualization plotOutline={plotOutline} />
              </Tabs.TabPane>
              <Tabs.TabPane tab="编辑剧情" key="edit">
                <PlotOutlineEditForm plotOutline={plotOutline} onUpdate={handlePlotUpdate} />
              </Tabs.TabPane>
            </Tabs>
          </div>
        )}
      </Modal>

      {/* 生成模态框 */}
      <Modal
        title="生成剧情大纲"
        open={showGenerateModal}
        onCancel={() => setShowGenerateModal(false)}
        footer={null}
        width={800}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleGeneratePlot}
        >
          <Form.Item
            name="worldview_id"
            label="选择世界观"
            rules={[{ required: true, message: '请选择世界观' }]}
          >
            <Select 
              placeholder="请选择世界观" 
              showSearch
              optionFilterProp="children"
              filterOption={(input, option) => {
                const worldView = worldViews.find(w => w.worldview_id === option?.value);
                if (!worldView) return false;
                return worldView.name.toLowerCase().includes(input.toLowerCase()) ||
                       worldView.core_concept.toLowerCase().includes(input.toLowerCase());
              }}
              optionLabelProp="label"
            >
              {worldViews.map((worldView) => (
                <Option 
                  key={worldView.worldview_id} 
                  value={worldView.worldview_id}
                  label={worldView.name}
                >
                  <div>
                    <div style={{ fontWeight: 'bold' }}>{worldView.name}</div>
                    <div style={{ fontSize: '12px', color: '#666' }}>
                      {worldView.core_concept}
                    </div>
                  </div>
                </Option>
              ))}
            </Select>
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="title"
                label="小说标题"
                rules={[{ required: true, message: '请输入小说标题' }]}
              >
                <Input placeholder="请输入小说标题" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="tone"
                label="故事基调"
                rules={[{ required: true, message: '请选择故事基调' }]}
              >
                <Select placeholder="请选择故事基调">
                  <Option value="热血">热血</Option>
                  <Option value="轻松">轻松</Option>
                  <Option value="严肃">严肃</Option>
                  <Option value="幽默">幽默</Option>
                  <Option value="悬疑">悬疑</Option>
                  <Option value="神秘">神秘</Option>
                  <Option value="悲壮">悲壮</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Form.Item
            name="core_conflict"
            label="核心冲突"
            rules={[{ required: true, message: '请输入核心冲突' }]}
          >
            <TextArea rows={3} placeholder="请输入核心冲突，如：正邪之争、复仇之路等" />
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="theme"
                label="主题思想"
                rules={[{ required: true, message: '请输入主题思想' }]}
              >
                <Input placeholder="请输入主题思想，如：成长与正义" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="protagonist_character_id"
                label="主角角色"
                rules={[{ required: true, message: '请选择主角角色' }]}
              >
                <Select placeholder="请选择主角角色">
                  {characters.map(char => (
                    <Option key={char.id} value={char.id}>
                      {char.name} ({char.role_type})
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="narrative_structure"
                label="叙事结构"
                rules={[{ required: true, message: '请选择叙事结构' }]}
              >
                <Select placeholder="请选择叙事结构">
                  <Option value="线性叙事">线性叙事</Option>
                  <Option value="非线性叙事">非线性叙事</Option>
                  <Option value="多视角叙事">多视角叙事</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="story_structure"
                label="故事结构"
                rules={[{ required: true, message: '请选择故事结构' }]}
              >
                <Select placeholder="请选择故事结构">
                  <Option value="3幕式">3幕式</Option>
                  <Option value="5幕式">5幕式</Option>
                  <Option value="7幕式">7幕式</Option>
                  <Option value="英雄之旅">英雄之旅</Option>
                  <Option value="起承转合">起承转合</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="target_word_count"
                label="目标字数"
                rules={[{ required: true, message: '请输入目标字数' }]}
              >
                <InputNumber
                  style={{ width: '100%' }}
                  placeholder="目标字数"
                  min={10000}
                  max={1000000}
                  step={10000}
                />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="estimated_chapters"
                label="预估章节数"
                rules={[{ required: true, message: '请输入预估章节数' }]}
              >
                <InputNumber
                  style={{ width: '100%' }}
                  placeholder="预估章节数"
                  min={5}
                  max={200}
                  step={5}
                />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item style={{ marginBottom: 0, textAlign: 'right' }}>
            <Space>
              <Button onClick={() => setShowGenerateModal(false)}>
                取消
              </Button>
              <Button type="primary" htmlType="submit" loading={loading}>
                生成剧情大纲
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default PlotOutline;
