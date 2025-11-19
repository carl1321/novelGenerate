import React, { useState, useEffect } from 'react';
import { 
  Card, Button, Input, message, Spin, Typography, Space, 
  Table, Tag, Progress, Row, Col, Modal, Form,
  Select, InputNumber, Divider, Tooltip, Badge, Drawer,
  List, Avatar, Collapse, Empty, Pagination
} from 'antd';
import { 
  FileTextOutlined, EyeOutlined, EditOutlined, DeleteOutlined,
  ClockCircleOutlined, UserOutlined, EnvironmentOutlined,
  ThunderboltOutlined, HeartOutlined, BulbOutlined,
  SettingOutlined, PlusOutlined, BookOutlined, SearchOutlined,
  FilterOutlined, SortAscendingOutlined, SortDescendingOutlined,
  PlayCircleOutlined, CalendarOutlined, LinkOutlined,
  RocketOutlined, StarOutlined
} from '@ant-design/icons';

const { Title, Paragraph, Text } = Typography;
const { TextArea } = Input;
const { Option } = Select;
const { Panel } = Collapse;

interface PlotOutline {
  id: string;
  title: string;
  description: string;
  theme: string;
  tone: string;
  genre: string;
  target_word_count: number;
  estimated_chapters: number;
  structure_type: string;
  narrative_structure: string;
  conflict_type: string;
  worldview_id: string;
  main_character_ids: string[];
  supporting_character_ids: string[];
  created_at: string;
  updated_at: string;
}

interface ChapterSummary {
  id: string;
  chapter_number: number;
  title: string;
  act_belonging: string;
  core_event: string;
  status: string;
  created_at: string;
  updated_at: string;
  scene_count: number;
  chapter_summary: string;
}

interface ForeshadowingItem {
  content: string;
  type: string;
  expected_resolution_chapter: number;
}

interface ChapterOutline {
  id: string;
  plot_outline_id: string;
  chapter_number: number;
  title: string;
  act_belonging: string;
  chapter_summary: string;
  core_event: string;
  key_scenes: Array<{
    scene_title: string;
    scene_description: string;
    event_relation: string;
  }>;
  writing_notes: string;
  status: string;
  created_at: string;
  updated_at: string;
}

// 事件接口定义
interface Event {
  id: string;
  title: string;
  description: string;
  event_type: string;
  importance: string;
  category: string;
  setting: string;
  participants: string[];
  duration: string;
  outcome: string;
  plot_impact: string;
  character_impact: Record<string, string>;
  foreshadowing_elements: string[];
  prerequisites: string[];
  consequences: string[];
  tags: string[];
  chapter_number?: number;
  sequence_order: number;
  created_at: string;
  // 增强字段
  story_position?: number;
  conflict_core?: string;
  dramatic_tension?: number;
  emotional_impact?: number;
  chapter_integration_points?: string[];
  storyline_requirements?: string[];
}

const ChapterOutline: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [summaries, setSummaries] = useState<ChapterSummary[]>([]);
  const [selectedChapter, setSelectedChapter] = useState<ChapterOutline | null>(null);
  const [showChapterDetail, setShowChapterDetail] = useState(false);
  const [plotId, setPlotId] = useState<string>('');
  const [plotOutline, setPlotOutline] = useState<PlotOutline | null>(null);
  const [plotOutlines, setPlotOutlines] = useState<PlotOutline[]>([]);
  const [selectedPlotOutline, setSelectedPlotOutline] = useState<string>('');
  const [searchText, setSearchText] = useState<string>('');
  const [filterAct, setFilterAct] = useState<string>('');
  const [filterStatus, setFilterStatus] = useState<string>('');
  const [sortField, setSortField] = useState<string>('chapter_number');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [total, setTotal] = useState(0);
  const [showQuickGenerate, setShowQuickGenerate] = useState(false);
  const [quickGenerateText, setQuickGenerateText] = useState<string>('');
  const [showGenerateModal, setShowGenerateModal] = useState(false);
  const [form] = Form.useForm();
  const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([]);
  const [selectedChapters, setSelectedChapters] = useState<ChapterSummary[]>([]);
  const [showEditModal, setShowEditModal] = useState(false);
  const [editingChapter, setEditingChapter] = useState<ChapterSummary | null>(null);
  const [editForm] = Form.useForm();
  
  // 事件相关状态
  const [events, setEvents] = useState<Event[]>([]);
  const [eventIntegrationMode, setEventIntegrationMode] = useState<'auto' | 'manual' | 'none'>('auto');
  const [selectedEvents, setSelectedEvents] = useState<string[]>([]);
  const [showEventModal, setShowEventModal] = useState(false);

  // 初始化表单
  const initializeForm = () => {
    form.setFieldsValue({
      act_belonging: '第一幕 - 开端',
      chapter_count: 5,
      start_chapter: 1,
    });
  };

  // 处理剧情大纲选择变化
  const handlePlotOutlineChange = async (plotId: string) => {
    if (plotId) {
      // 获取剧情大纲详情
      const plotData = await fetchPlotOutline(plotId);
      // 获取相关事件
      await fetchEvents(plotId);
    }
  };

  // 编辑章节
  const handleEditChapter = async (chapter: ChapterSummary) => {
    setEditingChapter(chapter);
    
    // 确保事件列表已加载
    if (events.length === 0 && plotId) {
      await fetchEvents(plotId);
    }
    
    // 获取完整的章节数据（包含场景）
    try {
      const response = await fetch(`http://localhost:8001/api/v1/chapter/chapter-outlines/single/${chapter.id}`);
      if (response.ok) {
        const fullChapter = await response.json();
        editForm.setFieldsValue({
          title: fullChapter.title,
          chapter_summary: fullChapter.chapter_summary,
          act_belonging: fullChapter.act_belonging,
          core_event: fullChapter.core_event,
          key_scenes: fullChapter.key_scenes || [],
        });
      } else {
        // 如果获取失败，使用摘要数据
        editForm.setFieldsValue({
          title: chapter.title,
          chapter_summary: chapter.chapter_summary,
          act_belonging: chapter.act_belonging,
          core_event: chapter.core_event,
          key_scenes: [],
        });
      }
    } catch (error) {
      console.error('获取章节详情失败:', error);
      // 使用摘要数据
      editForm.setFieldsValue({
        title: chapter.title,
        chapter_summary: chapter.chapter_summary,
        act_belonging: chapter.act_belonging,
        core_event: chapter.core_event,
        key_scenes: [],
      });
    }
    
    setShowEditModal(true);
  };

  // 保存编辑
  const handleSaveEdit = async (values: any) => {
    if (!editingChapter) return;

    setLoading(true);
    try {
      // 构建完整的章节对象
      const updatedChapter = {
        ...editingChapter,
        ...values,
        // 确保core_event字段正确保存
        core_event: values.core_event || '',
        updated_at: new Date().toISOString(),
      };

      const response = await fetch(`http://localhost:8001/api/v1/chapter/chapter-outlines/${editingChapter.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updatedChapter),
      });

      if (response.ok) {
        message.success('章节更新成功');
        setShowEditModal(false);
        setEditingChapter(null);
        editForm.resetFields();
        // 重新加载章节列表
        await fetchChapterSummaries(plotId);
      } else {
        const errorData = await response.json();
        message.error(`更新失败: ${errorData.detail || '未知错误'}`);
      }
    } catch (error) {
      message.error(`更新失败: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  // 批量删除章节
  const handleBatchDelete = async () => {
    if (selectedRowKeys.length === 0) {
      message.warning('请选择要删除的章节');
      return;
    }

    Modal.confirm({
      title: '确认批量删除',
      content: `确定要删除选中的 ${selectedRowKeys.length} 个章节吗？此操作不可恢复。`,
      okText: '删除',
      okType: 'danger',
      cancelText: '取消',
      onOk: async () => {
        setLoading(true);
        try {
          const deletePromises = selectedChapters.map(chapter => 
            fetch(`http://localhost:8001/api/v1/chapter/chapter-outlines/${chapter.id}`, {
              method: 'DELETE',
            })
          );
          
          const responses = await Promise.all(deletePromises);
          const failedCount = responses.filter(response => !response.ok).length;
          
          if (failedCount === 0) {
            message.success(`成功删除 ${selectedRowKeys.length} 个章节`);
            setSelectedRowKeys([]);
            setSelectedChapters([]);
            // 重新加载章节列表
            await fetchChapterSummaries(plotId);
          } else {
            message.error(`删除失败，有 ${failedCount} 个章节删除失败`);
          }
        } catch (error) {
          message.error(`批量删除失败: ${error.message}`);
        } finally {
          setLoading(false);
        }
      },
    });
  };

  // 删除章节
  const handleDeleteChapter = async (chapterId: string, chapterNumber: number) => {
    Modal.confirm({
      title: '确认删除',
      content: `确定要删除第${chapterNumber}章吗？此操作不可恢复。`,
      okText: '删除',
      okType: 'danger',
      cancelText: '取消',
      onOk: async () => {
        try {
          const response = await fetch(`http://localhost:8001/api/v1/chapter/chapter-outlines/${chapterId}`, {
            method: 'DELETE',
          });
          
          if (response.ok) {
            message.success('章节删除成功');
            // 重新加载章节列表
            await fetchChapterSummaries(plotId);
          } else {
            const errorData = await response.json();
            message.error(`删除失败: ${errorData.detail || '未知错误'}`);
          }
        } catch (error) {
          message.error(`删除失败: ${error.message}`);
        }
      },
    });
  };

  // 获取所有剧情大纲列表
  const fetchPlotOutlines = async () => {
    try {
      const response = await fetch('http://localhost:8001/api/v1/plot/plot-outlines');
      if (response.ok) {
        const data = await response.json();
        setPlotOutlines(data);
        
        // 如果有剧情大纲，自动选择第一个
        if (data && data.length > 0) {
          const firstPlot = data[0];
          setPlotId(firstPlot.id);
          setSelectedPlotOutline(firstPlot.id);
          // 获取章节列表
          await fetchChapterSummaries(firstPlot.id);
          // 获取剧情大纲详情
          await fetchPlotOutline(firstPlot.id);
          // 获取事件列表
          await fetchEvents(firstPlot.id);
        }
      } else {
        message.error('获取剧情大纲列表失败');
      }
    } catch (error) {
      message.error('获取剧情大纲列表失败');
    }
  };

  // 获取事件列表
  const fetchEvents = async (plotId?: string) => {
    try {
      let url = 'http://localhost:8001/api/v1/events';
      if (plotId) {
        url += `?plot_outline_id=${plotId}`;
      }
      
      const response = await fetch(url);
      if (response.ok) {
        const data = await response.json();
        setEvents(data || []);
      }
    } catch (error) {
      console.error('获取事件列表失败:', error);
    }
  };


  // 获取剧情大纲信息
  const fetchPlotOutline = async (plotId: string) => {
    try {
      const response = await fetch(`http://localhost:8001/api/v1/plot/plot-outlines/${plotId}`);
      if (response.ok) {
        const data = await response.json();
        setPlotOutline(data);
        return data;
      } else {
        message.error('获取剧情大纲失败');
        return null;
      }
    } catch (error) {
      message.error('获取剧情大纲失败');
      return null;
    }
  };

  // 组件加载时获取剧情大纲列表
  useEffect(() => {
    fetchPlotOutlines();
  }, []);

  // 获取章节摘要列表
  const fetchChapterSummaries = async (selectedPlotId?: string) => {
    const targetPlotId = selectedPlotId || plotId;
    if (!targetPlotId) return;
    
    setLoading(true);
    try {
      const response = await fetch(`http://localhost:8001/api/v1/chapter/chapter-outlines/summary/${targetPlotId}`);
      if (response.ok) {
        const data = await response.json();
        setSummaries(data.summaries);
        setTotal(data.total);
      } else {
        message.error('获取章节列表失败');
        setSummaries([]);
        setTotal(0);
      }
    } catch (error) {
      message.error('获取章节列表失败');
      setSummaries([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  };


  // 一句话快速生成章节大纲
  const handleQuickGenerate = async () => {
    if (!plotId || !quickGenerateText.trim()) {
      message.warning('请输入生成要求');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch('http://localhost:8001/api/v1/chapter/chapter-outlines/simple', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          plot_outline_id: plotId,
          additional_requirements: quickGenerateText,
        }),
        signal: AbortSignal.timeout(600000),
      });

      if (!response.ok) {
        throw new Error('生成失败');
      }

      const data = await response.json();
      if (data.success) {
        message.success(`成功生成${data.chapters.length}个章节大纲！`);
        setShowQuickGenerate(false);
        setQuickGenerateText('');
        // 重新加载章节列表
        await fetchChapterSummaries();
      } else {
        throw new Error(data.message);
      }
    } catch (error) {
      message.error(`生成失败: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  // 生成章节大纲
  const handleGenerateChapters = async (values: any) => {
    setLoading(true);
    try {
      const requestData = {
        plot_outline_id: plotId,
        event_integration_mode: eventIntegrationMode,
        chapter_count: values.chapter_count,
        start_chapter: values.start_chapter,
        act_belonging: values.act_belonging,
        additional_requirements: values.description,
        generate_event_mappings: eventIntegrationMode !== 'none'
      };

      const response = await fetch('http://localhost:8001/api/v1/chapter/chapter-outlines', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData),
        signal: AbortSignal.timeout(600000),
      });

      if (!response.ok) {
        throw new Error('生成失败');
      }

      const data = await response.json();
      if (data.success) {
        message.success(`成功生成${data.chapters.length}个章节大纲！`);
        setShowGenerateModal(false);
        form.resetFields();
        // 重新加载章节列表
        await fetchChapterSummaries();
      } else {
        throw new Error(data.message);
      }
    } catch (error) {
      message.error(`生成失败: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  // 获取单个章节详情
  const fetchChapterDetail = async (chapterId: string) => {
    setLoading(true);
    try {
      const response = await fetch(`http://localhost:8001/api/v1/chapter/chapter-outlines/single/${chapterId}`);
      if (response.ok) {
        const data = await response.json();
        setSelectedChapter(data);
        setShowChapterDetail(true);
      } else {
        message.error('获取章节详情失败');
      }
    } catch (error) {
      message.error('获取章节详情失败');
    } finally {
      setLoading(false);
    }
  };

  // 过滤和排序数据
  const getFilteredAndSortedData = () => {
    let filtered = summaries.filter(chapter => {
      const matchesSearch = !searchText || 
        chapter.title.toLowerCase().includes(searchText.toLowerCase()) ||
        chapter.chapter_summary.toLowerCase().includes(searchText.toLowerCase());
      
      const matchesAct = !filterAct || chapter.act_belonging === filterAct;
      const matchesStatus = !filterStatus || chapter.status === filterStatus;
      
      return matchesSearch && matchesAct && matchesStatus;
    });

    // 排序
    filtered.sort((a, b) => {
      let aValue = a[sortField as keyof ChapterSummary];
      let bValue = b[sortField as keyof ChapterSummary];
      
      if (typeof aValue === 'string') {
        aValue = aValue.toLowerCase();
        bValue = (bValue as string).toLowerCase();
      }
      
      if (sortOrder === 'asc') {
        return aValue < bValue ? -1 : aValue > bValue ? 1 : 0;
      } else {
        return aValue > bValue ? -1 : aValue < bValue ? 1 : 0;
      }
    });

    return filtered;
  };

  // 表格列定义
  const columns = [
    {
      title: '章节',
      dataIndex: 'chapter_number',
      key: 'chapter_number',
      width: 80,
      render: (chapterNumber: number) => (
        <Badge count={chapterNumber} style={{ backgroundColor: '#1890ff' }} />
      ),
    },
    {
      title: '标题',
      dataIndex: 'title',
      key: 'title',
      ellipsis: true,
      render: (title: string, record: ChapterSummary) => (
        <div>
          <Text strong>{title}</Text>
          <br />
          <Text type="secondary" style={{ fontSize: '12px' }}>
            {record.chapter_summary}
          </Text>
        </div>
      ),
    },
    {
      title: '所属幕次',
      dataIndex: 'act_belonging',
      key: 'act_belonging',
      width: 100,
      render: (act: string) => (
        <Tag color="green">{act}</Tag>
      ),
    },
    {
      title: '核心事件',
      dataIndex: 'core_event',
      key: 'core_event',
      width: 120,
      render: (coreEvent: string) => (
        <Tag color="blue">{coreEvent || '未指定'}</Tag>
      ),
    },
    {
      title: '场景数',
      dataIndex: 'scene_count',
      key: 'scene_count',
      width: 80,
      render: (count: number) => (
        <Tag color="purple">{count}</Tag>
      ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 80,
      render: (status: string) => {
        const colorMap: { [key: string]: string } = {
          'draft': 'default',
          'completed': 'success',
          'reviewing': 'processing',
          'published': 'blue'
        };
        return <Tag color={colorMap[status] || 'default'}>{status}</Tag>;
      },
    },
    {
      title: '事件关联',
      key: 'events',
      width: 100,
      render: (_, record: ChapterSummary) => {
        const chapterEvents = events.filter(event => event.chapter_number === record.chapter_number);
        return (
          <Space>
            {chapterEvents.length > 0 ? (
              <Tooltip title={`关联${chapterEvents.length}个事件`}>
                <Badge count={chapterEvents.length} size="small">
                  <CalendarOutlined style={{ color: '#1890ff' }} />
                </Badge>
              </Tooltip>
            ) : (
              <Tooltip title="无关联事件">
                <CalendarOutlined style={{ color: '#d9d9d9' }} />
              </Tooltip>
            )}
          </Space>
        );
      },
    },
    {
      title: '操作',
      key: 'actions',
      width: 150,
      render: (_, record: ChapterSummary) => (
        <Space>
          <Tooltip title="查看详情">
            <Button 
              type="text" 
              icon={<EyeOutlined />} 
              onClick={() => fetchChapterDetail(record.id)}
            />
          </Tooltip>
          <Tooltip title="编辑">
            <Button 
              type="text" 
              icon={<EditOutlined />} 
              onClick={() => handleEditChapter(record)}
            />
          </Tooltip>
          <Tooltip title="查看事件">
            <Button
              type="text"
              icon={<CalendarOutlined />}
              onClick={() => {
                const chapterEvents = events.filter(event => event.chapter_number === record.chapter_number);
                if (chapterEvents.length > 0) {
                  setShowEventModal(true);
                  // 这里可以设置选中的事件
                } else {
                  message.info('该章节暂无关联事件');
                }
              }}
            />
          </Tooltip>
          <Tooltip title="删除">
            <Button 
              type="text" 
              icon={<DeleteOutlined />} 
              danger 
              onClick={() => handleDeleteChapter(record.id, record.chapter_number)}
            />
          </Tooltip>
        </Space>
      ),
    },
  ];

  // 章节详情抽屉
  const ChapterDetailDrawer = () => (
    <Drawer
      title={`第${selectedChapter?.chapter_number}章 - ${selectedChapter?.title}`}
      placement="right"
      width={600}
      open={showChapterDetail}
      onClose={() => setShowChapterDetail(false)}
    >
      {selectedChapter && (
        <div>
          {/* 基本信息 */}
          <Card title="基本信息" size="small" style={{ marginBottom: 16 }}>
            <Row gutter={[16, 8]}>
              <Col span={12}>
                <Text strong>所属幕次：</Text>
                <Tag color="blue">{selectedChapter.act_belonging}</Tag>
              </Col>
              <Col span={12}>
                <Text strong>核心事件：</Text>
                {selectedChapter.core_event ? (
                  <Tag 
                    color="green" 
                    style={{ cursor: 'pointer' }}
                    onClick={() => {
                      // 查找对应的事件详情，支持事件ID和事件标题
                      const event = events.find(e => 
                        e.id === selectedChapter.core_event || 
                        e.title === selectedChapter.core_event
                      );
                      if (event) {
                        message.info(`事件详情：${event.description.substring(0, 100)}...`);
                      } else {
                        message.warning('未找到对应的事件详情');
                      }
                    }}
                  >
                    {selectedChapter.core_event}
                  </Tag>
                ) : (
                  <Tag color="red">未指定</Tag>
                )}
              </Col>
              <Col span={12}>
                <Text strong>状态：</Text>
                <Tag color="cyan">{selectedChapter.status}</Tag>
              </Col>
            </Row>
          </Card>

          {/* 章节概要 */}
          <Card title="章节概要" size="small" style={{ marginBottom: 16 }}>
            <Paragraph>{selectedChapter.chapter_summary}</Paragraph>
          </Card>

          {/* 关键场景 */}
          <Card title="关键场景" size="small" style={{ marginBottom: 16 }}>
            {selectedChapter.key_scenes && selectedChapter.key_scenes.length > 0 ? (
              <div>
                {selectedChapter.key_scenes.map((scene, index) => (
                  <Card key={index} size="small" style={{ marginBottom: 8 }}>
                    <Row gutter={[8, 4]}>
                      <Col span={24}>
                        <Text strong>场景{index + 1}：{scene.scene_title}</Text>
                      </Col>
                      <Col span={24}>
                        <Text>{scene.scene_description}</Text>
                      </Col>
                    </Row>
                  </Card>
                ))}
              </div>
            ) : (
              <Text type="secondary">暂无关键场景</Text>
            )}
          </Card>

        </div>
      )}
    </Drawer>
  );

  const filteredData = getFilteredAndSortedData();
  const paginatedData = filteredData.slice(
    (currentPage - 1) * pageSize,
    currentPage * pageSize
  );

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <Title level={2}>
          <BookOutlined style={{ marginRight: 8 }} />
          章节大纲管理
        </Title>
        <Paragraph style={{ fontSize: 16, color: '#666' }}>
          选择剧情大纲，管理和生成详细的章节大纲，包括场景设计、角色发展和写作指导。
        </Paragraph>
      </div>

      {/* 剧情大纲选择器 */}
      <Card title="选择剧情大纲" style={{ marginBottom: 24 }}>
        <Row gutter={16}>
          <Col span={12}>
            <Select
              placeholder="请选择剧情大纲"
              value={selectedPlotOutline}
              onChange={(value) => {
                setSelectedPlotOutline(value);
                setPlotId(value);
                setSelectedRowKeys([]);
                setSelectedChapters([]);
                fetchChapterSummaries(value);
                fetchPlotOutline(value);
              }}
              style={{ width: '100%' }}
              showSearch
              filterOption={(input, option) =>
                (option?.children as string)?.toLowerCase().includes(input.toLowerCase())
              }
            >
              {plotOutlines.map((plot) => (
                <Option key={plot.id} value={plot.id}>
                  {plot.title}
                </Option>
              ))}
            </Select>
          </Col>
          <Col span={12}>
            <Text type="secondary">
              选择剧情大纲后，将显示该大纲下的所有章节信息
            </Text>
          </Col>
        </Row>
      </Card>

      {/* 生成按钮 */}
      <Card style={{ marginBottom: 24 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <Title level={3} style={{ margin: 0 }}>
              <PlayCircleOutlined style={{ marginRight: 8 }} />
              生成章节大纲
            </Title>
            <Text type="secondary">
              基于事件智能生成章节大纲，支持事件融入和角色选择
            </Text>
          </div>
          <Space>
            <Button
              type="primary"
              size="large"
              icon={<PlayCircleOutlined />}
              onClick={() => setShowGenerateModal(true)}
              style={{ height: 50, fontSize: 16 }}
            >
              生成章节大纲
            </Button>
          </Space>
        </div>
      </Card>

      {/* 章节列表表格 */}
      <Card 
        title={
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Space>
              <span>章节列表 {summaries.length > 0 ? `(${summaries.length}章)` : ''}</span>
              {selectedRowKeys.length > 0 && (
                <>
                  <Text type="secondary">
                    已选择 {selectedRowKeys.length} 个章节
                  </Text>
                  <Button 
                    danger 
                    onClick={handleBatchDelete}
                    loading={loading}
                    icon={<DeleteOutlined />}
                    size="small"
                  >
                    批量删除
                  </Button>
                </>
              )}
            </Space>
          </div>
        }
      >
        {!plotId ? (
          <Empty 
            description="请先选择剧情大纲"
            image={Empty.PRESENTED_IMAGE_SIMPLE}
          />
        ) : summaries.length === 0 ? (
          <Empty 
            description="该剧情大纲下暂无章节，请先生成章节"
            image={Empty.PRESENTED_IMAGE_SIMPLE}
          />
        ) : (
          <>
            {/* 搜索和过滤器 */}
            <Row gutter={16} style={{ marginBottom: 16 }}>
              <Col span={8}>
                <Input
                  placeholder="搜索章节标题或概要"
                  prefix={<SearchOutlined />}
                  value={searchText}
                  onChange={(e) => setSearchText(e.target.value)}
                  allowClear
                />
              </Col>
              <Col span={6}>
                <Select
                  placeholder="按幕次筛选"
                  value={filterAct}
                  onChange={setFilterAct}
                  allowClear
                  style={{ width: '100%' }}
                >
                  <Option value="第一幕 - 开端">第一幕 - 开端</Option>
                  <Option value="第二幕 - 发展">第二幕 - 发展</Option>
                  <Option value="第三幕 - 高潮">第三幕 - 高潮</Option>
                  <Option value="第四幕 - 结局">第四幕 - 结局</Option>
                  <Option value="第五幕 - 尾声">第五幕 - 尾声</Option>
                </Select>
              </Col>
              <Col span={6}>
                <Select
                  placeholder="按状态筛选"
                  value={filterStatus}
                  onChange={setFilterStatus}
                  allowClear
                  style={{ width: '100%' }}
                >
                  <Option value="大纲">大纲</Option>
                  <Option value="草稿">草稿</Option>
                  <Option value="已完成">已完成</Option>
                </Select>
              </Col>
              <Col span={4}>
                <Button
                  icon={<FilterOutlined />}
                  onClick={() => {
                    setSearchText('');
                    setFilterAct('');
                    setFilterStatus('');
                  }}
                >
                  清除筛选
                </Button>
              </Col>
            </Row>
            
            <Table
              columns={columns}
              dataSource={paginatedData}
              rowKey="id"
              rowSelection={{
                selectedRowKeys: selectedRowKeys,
                onChange: (selectedRowKeys: React.Key[], selectedRows: ChapterSummary[]) => {
                  setSelectedRowKeys(selectedRowKeys);
                  setSelectedChapters(selectedRows);
                },
                getCheckboxProps: (record: ChapterSummary) => ({
                  name: record.title,
                }),
                selections: [
                  {
                    key: 'all',
                    text: '全选当前页',
                    onSelect: () => {
                      setSelectedRowKeys(paginatedData.map(item => item.id));
                      setSelectedChapters(paginatedData);
                    },
                  },
                  {
                    key: 'none',
                    text: '取消全选',
                    onSelect: () => {
                      setSelectedRowKeys([]);
                      setSelectedChapters([]);
                    },
                  },
                ],
              }}
              pagination={{
                current: currentPage,
                pageSize: pageSize,
                total: filteredData.length,
                showSizeChanger: true,
                showQuickJumper: true,
                showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条，共 ${total} 条`,
                onChange: (page, size) => {
                  setCurrentPage(page);
                  setPageSize(size);
                }
              }}
            />
          </>
        )}
      </Card>

      {/* 生成章节大纲模态框 */}
      <Modal
        title="生成章节大纲"
        open={showGenerateModal}
        onCancel={() => setShowGenerateModal(false)}
        footer={null}
        width={800}
        afterOpenChange={(open) => {
          if (open) {
            initializeForm();
          }
        }}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleGenerateChapters}
        >
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="plot_outline_id"
                label="选择剧情大纲"
                rules={[{ required: true, message: '请选择剧情大纲' }]}
              >
                <Select
                  placeholder="请选择剧情大纲"
                  showSearch
                  onChange={handlePlotOutlineChange}
                  filterOption={(input, option) =>
                    (option?.children as string)?.toLowerCase().includes(input.toLowerCase())
                  }
                >
                  {plotOutlines.map((plot) => (
                    <Option key={plot.id} value={plot.id}>
                      {plot.title} - {plot.genre}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="act_belonging"
                label="选择幕次"
                rules={[{ required: true, message: '请选择幕次' }]}
              >
                <Select placeholder="请选择要生成章节的幕次">
                  <Option value="第一幕 - 开端">第一幕 - 开端</Option>
                  <Option value="第二幕 - 发展">第二幕 - 发展</Option>
                  <Option value="第三幕 - 高潮">第三幕 - 高潮</Option>
                  <Option value="第四幕 - 结局">第四幕 - 结局</Option>
                  <Option value="第五幕 - 尾声">第五幕 - 尾声</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="chapter_count"
                label="生成章节数"
                rules={[{ required: true, message: '请输入要生成的章节数' }]}
              >
                <InputNumber
                  min={1}
                  max={20}
                  placeholder="请输入要生成的章节数"
                  style={{ width: '100%' }}
                />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="start_chapter"
                label="起始章节号"
                rules={[{ required: true, message: '请输入起始章节号' }]}
              >
                <InputNumber
                  min={1}
                  max={100}
                  placeholder="请输入起始章节号"
                  style={{ width: '100%' }}
                />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item
            name="description"
            label="章节大纲描述"
            rules={[{ required: true, message: '请输入章节大纲描述' }]}
          >
            <TextArea
              rows={4}
              placeholder="请描述您希望生成的章节内容，例如：主角初入修仙界，遇到师父，学习基础功法，第一次战斗等情节"
            />
          </Form.Item>

          <Divider>事件驱动配置</Divider>
              
              <Form.Item label="事件融入模式">
                <Select
                  value={eventIntegrationMode}
                  onChange={setEventIntegrationMode}
                  style={{ width: '100%' }}
                >
                  <Option value="auto">自动融入 - AI自动选择相关事件</Option>
                  <Option value="manual">手动选择 - 用户手动选择要融入的事件</Option>
                  <Option value="none">无融入 - 传统生成方式</Option>
                </Select>
                <Text type="secondary" style={{ display: 'block', marginTop: 4 }}>
                  {eventIntegrationMode === 'auto' && 'AI将自动分析事件，选择最适合的事件融入章节'}
                  {eventIntegrationMode === 'manual' && '您需要手动选择要融入章节的事件'}
                  {eventIntegrationMode === 'none' && '使用传统方式生成章节，不考虑事件融入'}
                </Text>
              </Form.Item>

              {eventIntegrationMode === 'manual' && (
                <Form.Item label="选择要融入的事件">
                  <Select
                    mode="multiple"
                    placeholder="选择要融入章节的事件"
                    value={selectedEvents}
                    onChange={setSelectedEvents}
                    allowClear
                    maxTagCount={3}
                    style={{ width: '100%' }}
                  >
                    {events.map((event) => (
                      <Option key={event.id} value={event.id}>
                        {event.title} ({event.event_type})
                      </Option>
                    ))}
                  </Select>
                  <Text type="secondary" style={{ display: 'block', marginTop: 4 }}>
                    已选择 {selectedEvents.length} 个事件
                  </Text>
                </Form.Item>
              )}


              {events.length > 0 && (
                <Card title="可用事件预览" size="small" style={{ marginTop: 16 }}>
                  <List
                    size="small"
                    dataSource={events.slice(0, 5)}
                    renderItem={(event) => (
                      <List.Item>
                        <Space>
                          <Text strong>{event.title}</Text>
                          <Tag color="blue">{event.importance}</Tag>
                          <Tag color="green">{event.event_type}</Tag>
                          {event.dramatic_tension && (
                            <Tag color="orange">张力: {event.dramatic_tension}/10</Tag>
                          )}
                        </Space>
                      </List.Item>
                    )}
                  />
                  {events.length > 5 && (
                    <Text type="secondary">还有 {events.length - 5} 个事件...</Text>
                  )}
                </Card>
              )}

          <Form.Item
            name="chapter_numbers"
            label="指定章节编号（可选）"
            help="留空则生成所有章节，指定则用逗号分隔，如：1,2,3"
          >
            <Input placeholder="例如：1,2,3 或留空生成所有章节" />
          </Form.Item>

          <Form.Item style={{ marginBottom: 0, textAlign: 'right' }}>
            <Space>
              <Button onClick={() => setShowGenerateModal(false)}>
                取消
              </Button>
              <Button type="primary" htmlType="submit" loading={loading}>
                生成章节大纲
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* 编辑章节模态框 */}
      <Modal
        title={`编辑第${editingChapter?.chapter_number}章`}
        open={showEditModal}
        onCancel={() => {
          setShowEditModal(false);
          setEditingChapter(null);
          editForm.resetFields();
        }}
        footer={null}
        width={800}
      >
        <Form
          form={editForm}
          layout="vertical"
          onFinish={handleSaveEdit}
        >
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="title"
                label="章节标题"
                rules={[{ required: true, message: '请输入章节标题' }]}
              >
                <Input placeholder="请输入章节标题" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="act_belonging"
                label="所属幕次"
                rules={[{ required: true, message: '请选择所属幕次' }]}
              >
                <Select placeholder="请选择所属幕次">
                  <Option value="第一幕 - 开端">第一幕 - 开端</Option>
                  <Option value="第二幕 - 发展">第二幕 - 发展</Option>
                  <Option value="第三幕 - 高潮">第三幕 - 高潮</Option>
                  <Option value="第四幕 - 结局">第四幕 - 结局</Option>
                  <Option value="第五幕 - 尾声">第五幕 - 尾声</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Form.Item
            name="chapter_summary"
            label="章节概要"
            rules={[{ required: true, message: '请输入章节概要' }]}
          >
            <TextArea
              rows={4}
              placeholder="请输入章节概要"
            />
          </Form.Item>

          <Form.Item
            name="core_event"
            label="核心事件"
            rules={[{ required: true, message: '请选择核心事件' }]}
          >
            <Select
              placeholder="请选择核心事件"
              showSearch
              filterOption={(input, option) =>
                (option?.children as string)?.toLowerCase().includes(input.toLowerCase())
              }
              allowClear
            >
              {events.map(event => (
                <Option key={event.id} value={event.title}>
                  {event.title} ({event.event_type})
                </Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item
            name="key_scenes"
            label="关键场景"
            rules={[{ required: true, message: '请至少添加一个关键场景' }]}
          >
            <Form.List name="key_scenes">
              {(fields, { add, remove }) => (
                <>
                  {fields.map(({ key, name, ...restField }) => (
                    <Card key={key} size="small" style={{ marginBottom: 8 }}>
                      <Row gutter={[8, 4]}>
                        <Col span={24}>
                          <Text strong>场景 {name + 1}</Text>
                        </Col>
                        <Col span={24}>
                          <Form.Item
                            {...restField}
                            name={[name, 'scene_title']}
                            rules={[{ required: true, message: '请输入场景标题' }]}
                            style={{ marginBottom: 8 }}
                          >
                            <Input placeholder="场景标题" />
                          </Form.Item>
                        </Col>
                        <Col span={24}>
                          <Form.Item
                            {...restField}
                            name={[name, 'scene_description']}
                            rules={[{ required: true, message: '请输入场景描述' }]}
                            style={{ marginBottom: 8 }}
                          >
                            <TextArea
                              rows={3}
                              placeholder="场景描述"
                            />
                          </Form.Item>
                        </Col>
                        <Col span={24} style={{ textAlign: 'right' }}>
                          <Button
                            type="link"
                            danger
                            onClick={() => remove(name)}
                            icon={<DeleteOutlined />}
                          >
                            删除场景
                          </Button>
                        </Col>
                      </Row>
                    </Card>
                  ))}
                  <Form.Item>
                    <Button
                      type="dashed"
                      onClick={() => add()}
                      block
                      icon={<PlusOutlined />}
                    >
                      添加场景
                    </Button>
                  </Form.Item>
                </>
              )}
            </Form.List>
          </Form.Item>

          <Form.Item style={{ marginBottom: 0, textAlign: 'right' }}>
            <Space>
              <Button onClick={() => {
                setShowEditModal(false);
                setEditingChapter(null);
                editForm.resetFields();
              }}>
                取消
              </Button>
              <Button type="primary" htmlType="submit" loading={loading}>
                保存修改
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* 章节详情抽屉 */}
      <ChapterDetailDrawer />

      {/* 事件模态框 */}
      <Modal
        title="章节关联事件"
        open={showEventModal}
        onCancel={() => setShowEventModal(false)}
        footer={[
          <Button key="close" onClick={() => setShowEventModal(false)}>
            关闭
          </Button>
        ]}
        width={800}
      >
        <List
          dataSource={events.filter(event => event.chapter_number)}
          renderItem={(event) => (
            <List.Item
              actions={[
                <Button type="link" icon={<EyeOutlined />}>
                  查看详情
                </Button>
              ]}
            >
              <List.Item.Meta
                title={
                  <Space>
                    <Text strong>{event.title}</Text>
                    <Tag color="blue">{event.importance}</Tag>
                    <Tag color="green">{event.event_type}</Tag>
                  </Space>
                }
                description={
                  <Space direction="vertical" size="small">
                    <Text>{event.description}</Text>
                    <Space>
                      {event.dramatic_tension && (
                        <Tag color="orange">张力: {event.dramatic_tension}/10</Tag>
                      )}
                      {event.emotional_impact && (
                        <Tag color="red">冲击: {event.emotional_impact}/10</Tag>
                      )}
                      <Text type="secondary">第{event.chapter_number}章</Text>
                    </Space>
                  </Space>
                }
              />
            </List.Item>
          )}
        />
      </Modal>
    </div>
  );
};

export default ChapterOutline;
