import React, { useState, useEffect } from 'react';
import {
  Card,
  Table,
  Button,
  Input,
  Select,
  Space,
  Tag,
  Modal,
  Form,
  InputNumber,
  message,
  Typography,
  Row,
  Col,
  Descriptions,
  Divider,
  Popconfirm,
  Tooltip,
  Empty,
  Statistic,
  Slider,
  Switch,
  Tabs,
  Badge,
  Progress,
  Alert,
  Drawer,
  List
} from 'antd';
import {
  CalendarOutlined,
  PlusOutlined,
  SearchOutlined,
  FilterOutlined,
  EyeOutlined,
  DeleteOutlined,
  EditOutlined,
  ReloadOutlined,
  PlayCircleOutlined,
  SettingOutlined,
  ThunderboltOutlined,
  HeartOutlined,
  StarOutlined,
  RocketOutlined,
  BarChartOutlined,
  TrophyOutlined,
  SyncOutlined,
  HistoryOutlined,
  FileTextOutlined,
  DiffOutlined
} from '@ant-design/icons';

const { Title, Text } = Typography;
const { Option } = Select;
const { TextArea } = Input;
const { TabPane } = Tabs;

// 事件类型定义
interface Event {
  id: string;
  title: string;
  description: string;
  event_type: string;
  setting: string;
  participants: string[];
  duration: string;
  outcome: string;
  plot_impact: string;
  character_impact: Record<string, string>;
  foreshadowing_elements: string[];
  chapter_number?: number;
  sequence_order: number;
  plot_outline_id?: string;
  created_at: string;
  // 版本管理字段
  version?: number;
  is_current_version?: boolean;
  // 核心字段
  story_position?: number;
  conflict_core?: string;
  dramatic_tension?: number;
  emotional_impact?: number;
}

// 事件生成请求
interface EventRequest {
  plot_outline_id: string;
  worldview_id?: string;
  importance_distribution: Record<string, number>;
  event_requirements: string;
  selected_act?: {
    act_number: number;
    act_name: string;
    core_mission: string;
  };
  story_tone?: string;
  narrative_structure?: string;
}

// 重要性分布配置
interface ImportanceDistribution {
  major: number;      // 重大事件
  conflict: number;   // 冲突事件
  special: number;    // 特殊事件
  daily: number;      // 日常事件
}

interface PlotOutline {
  id: string;
  title: string;
}

// 事件评分接口
interface EventScore {
  protagonist_involvement: number;
  plot_coherence: number;
  writing_quality: number;
  dramatic_tension: number;
  overall_quality: number;
  feedback: string;
  strengths: string[];
  weaknesses: string[];
}

// 进化历史接口
interface EvolutionHistory {
  id: number;
  original_event_id: string;
  evolved_event_id: string;
  score_id: number;
  evolution_reason: string;
  status: string;
  created_at: string;
  score_quality: number;
}

interface Act {
  act_number: number;
  act_name: string;
  core_mission: string;
  daily_events: string;
  conflict_events: string;
  special_events: string;
  major_events: string;
  stage_result: string;
}

interface PlotActs {
  plot_title: string;
  story_tone: string;
  narrative_structure: string;
  acts: Act[];
}

const Events: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [events, setEvents] = useState<Event[]>([]);
  const [plotOutlines, setPlotOutlines] = useState<PlotOutline[]>([]);
  const [worldViews, setWorldViews] = useState([]);
  const [selectedPlotOutline, setSelectedPlotOutline] = useState<string>('plot_5c4cc022');
  const [selectedWorldView, setSelectedWorldView] = useState<string>('');
  const [plotActs, setPlotActs] = useState<PlotActs | null>(null);
  const [selectedAct, setSelectedAct] = useState<Act | null>(null);
  const [searchText, setSearchText] = useState('');
  const [filterType, setFilterType] = useState('');
  const [filterImportance, setFilterImportance] = useState('');
  const [showGenerateModal, setShowGenerateModal] = useState(false);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [selectedEvent, setSelectedEvent] = useState<Event | null>(null);
  const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([]);
  const [selectedEvents, setSelectedEvents] = useState<Event[]>([]);
  const [generateForm] = Form.useForm();
  
  // 事件生成相关状态
  const [importanceDistribution, setImportanceDistribution] = useState<ImportanceDistribution>({
    major: 3,
    conflict: 5,
    daily: 10,
    special: 2
  });
  
  // 事件管理相关状态
  const [showDetailDrawer, setShowDetailDrawer] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showStatsModal, setShowStatsModal] = useState(false);
  const [editForm] = Form.useForm();
  const [activeTab, setActiveTab] = useState('list');
  
  // 事件评分与进化相关状态
  const [showScoreModal, setShowScoreModal] = useState(false);
  const [showEvolutionModal, setShowEvolutionModal] = useState(false);
  const [showEvolutionHistoryModal, setShowEvolutionHistoryModal] = useState(false);
  const [showEvolutionConfirmModal, setShowEvolutionConfirmModal] = useState(false); // 新增：进化确认弹窗
  const [currentScore, setCurrentScore] = useState<EventScore | null>(null);
  const [currentEvolutionHistory, setCurrentEvolutionHistory] = useState<EvolutionHistory[]>([]);
  const [scoringLoading, setScoringLoading] = useState<string | null>(null); // 改为存储正在评分的事件ID
  const [evolutionLoading, setEvolutionLoading] = useState<string | null>(null); // 改为存储正在进化的事件ID
  const [pendingEvolutionEventId, setPendingEvolutionEventId] = useState<string | null>(null); // 待进化的事件ID
  const [evolvedEvent, setEvolvedEvent] = useState<Event | null>(null); // 进化后的事件
  const [showEventDetailModal, setShowEventDetailModal] = useState(false); // 事件详情弹窗
  const [showEvolutionCompareModal, setShowEvolutionCompareModal] = useState(false); // 进化对比弹窗
  const [eventDetail, setEventDetail] = useState<any>(null); // 事件详情数据
  const [evolutionHistory, setEvolutionHistory] = useState<any>(null); // 进化历史数据
  const [customEvolutionDescription, setCustomEvolutionDescription] = useState(''); // 自定义进化描述

  // 事件类型选项
  const eventTypes = [
    '重大事件', '冲突事件', '特殊事件', '日常事件'
  ];

  const importanceLevels = ['重大事件', '冲突事件', '特殊事件', '日常事件'];

  // 获取世界观列表
  const fetchWorldViews = async () => {
    try {
      const response = await fetch('/api/v1/world/list');
      if (response.ok) {
      const data = await response.json();
      // 处理不同的数据格式
      if (Array.isArray(data)) {
        setWorldViews(data);
      } else if (data.worldviews && Array.isArray(data.worldviews)) {
        setWorldViews(data.worldviews);
      } else {
        setWorldViews([]);
      }
      }
    } catch (error) {
      console.error('获取世界观列表失败:', error);
    }
  };



  // 获取剧情大纲列表
  const fetchPlotOutlines = async () => {
    try {
      console.log('开始获取剧情大纲列表...');
      const response = await fetch('http://localhost:8001/api/v1/plot/plot-outlines');
      console.log('剧情大纲API响应状态:', response.status);
      if (response.ok) {
        const data = await response.json();
        console.log('剧情大纲数据:', data);
        setPlotOutlines(data || []);
      } else {
        console.error('剧情大纲API响应失败:', response.status);
      }
    } catch (error) {
      console.error('获取剧情大纲失败:', error);
    }
  };

  // 获取剧情大纲的幕次信息
  const fetchPlotActs = async (plotOutlineId: string) => {
    try {
      const response = await fetch(`http://localhost:8001/api/v1/events/plot/${plotOutlineId}/acts`);
      if (response.ok) {
        const data = await response.json();
        setPlotActs(data);
        setSelectedAct(null); // 重置选中的幕次
      } else {
        console.error('获取幕次信息失败:', response.status);
        setPlotActs(null);
      }
    } catch (error) {
      console.error('获取幕次信息失败:', error);
      setPlotActs(null);
    }
  };

  // 获取事件列表（带评分）
  const fetchEventsWithScores = async () => {
    console.log('开始获取带评分的事件列表');
    setLoading(true);
    try {
      if (selectedPlotOutline) {
        const response = await fetch(`http://localhost:8001/api/v1/events/${selectedPlotOutline}/with-scores`);
        console.log('带评分事件API响应状态:', response.status);
        if (response.ok) {
          const data = await response.json();
          console.log('带评分事件数据:', data);
          setEvents(data || []);
        } else {
          console.error('带评分事件API响应失败:', response.status);
          setEvents([]);
        }
      } else {
        // 如果没有选择剧情大纲，获取所有事件
        const response = await fetch('http://localhost:8001/api/v1/events');
        console.log('事件API响应状态:', response.status);
        if (response.ok) {
          const data = await response.json();
          console.log('事件数据:', data);
          setEvents(data || []);
        } else {
          console.error('事件API响应失败:', response.status);
          setEvents([]);
        }
      }
    } catch (error) {
      console.error('获取事件列表失败:', error);
      message.error('获取事件列表失败');
    } finally {
      setLoading(false);
    }
  };

  // 生成事件
  const handleGenerateEvents = async (values: any) => {
    if (!selectedPlotOutline) {
      message.warning('请选择剧情大纲');
      return;
    }

    setLoading(true);
    try {
      const requestData: EventRequest = {
        plot_outline_id: selectedPlotOutline,
        worldview_id: selectedWorldView || undefined,
        importance_distribution: {
          "重大事件": importanceDistribution.major,
          "冲突事件": importanceDistribution.conflict,
          "特殊事件": importanceDistribution.special,
          "日常事件": importanceDistribution.daily
        },
        event_requirements: values.event_requirements || '',
        selected_act: selectedAct ? {
          act_number: selectedAct.act_number,
          act_name: selectedAct.act_name,
          core_mission: selectedAct.core_mission,
          daily_events: selectedAct.daily_events,
          conflict_events: selectedAct.conflict_events,
          special_events: selectedAct.special_events,
          major_events: selectedAct.major_events
        } : undefined,
        story_tone: plotActs?.story_tone,
        narrative_structure: plotActs?.narrative_structure
      };

      const response = await fetch('http://localhost:8001/api/v1/events/enhanced', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData),
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          message.success(`成功生成${data.events.length}个事件`);
          setShowGenerateModal(false);
          generateForm.resetFields();
          await fetchEventsWithScores();
        } else {
          message.error(data.message || '生成失败');
        }
      } else {
        throw new Error('生成失败');
      }
    } catch (error) {
      message.error(`生成失败: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };


  // 删除事件
  const handleDeleteEvent = async (eventId: string, version?: number) => {
    try {
      let url = `http://localhost:8001/api/v1/events/${eventId}`;
      if (version) {
        url += `?version=${version}`;
      }
      
      const response = await fetch(url, {
        method: 'DELETE',
      });

      if (response.ok) {
        if (version) {
          message.success(`事件版本 v${version} 删除成功`);
        } else {
          message.success('事件删除成功');
        }
        // 重新获取事件列表
        await fetchEventsWithScores();
      } else {
        throw new Error('删除失败');
      }
    } catch (error) {
      message.error(`删除失败: ${error.message}`);
    }
  };

  // 查看事件详情
  const handleViewEvent = (event: Event) => {
    setSelectedEvent(event);
    setShowDetailModal(true);
  };

  // 查看事件详情（抽屉模式）
  const handleViewEventDrawer = async (event: Event) => {
    try {
      // 调用API获取最新版本（优先显示进化版本）
      const response = await fetch(`http://localhost:8001/api/v1/events/${event.id}/detail`);
      if (response.ok) {
        const data = await response.json();
        // 使用API返回的事件（可能是进化版本）
        setSelectedEvent(data.event);
        setShowDetailDrawer(true);
      } else {
        // 如果API失败，使用原始事件
        setSelectedEvent(event);
        setShowDetailDrawer(true);
      }
    } catch (error) {
      console.error('获取事件详情失败:', error);
      // 如果出错，使用原始事件
      setSelectedEvent(event);
      setShowDetailDrawer(true);
    }
  };

  // 编辑事件
  const handleEdit = async (event: Event) => {
    try {
      // 调用API获取最新版本（优先显示进化版本）
      const response = await fetch(`http://localhost:8001/api/v1/events/${event.id}/detail`);
      if (response.ok) {
        const data = await response.json();
        // 使用API返回的事件（可能是进化版本）
        const latestEvent = data.event;
        setSelectedEvent(latestEvent);
        
        // 只设置描述和结果字段
        const formValues = {
          description: latestEvent.description,
          outcome: latestEvent.outcome
        };
        
        editForm.setFieldsValue(formValues);
        setShowEditModal(true);
      } else {
        // 如果API失败，使用原始事件
        setSelectedEvent(event);
        
        // 只设置描述和结果字段
        const formValues = {
          description: event.description,
          outcome: event.outcome
        };
        
        editForm.setFieldsValue(formValues);
        setShowEditModal(true);
      }
    } catch (error) {
      console.error('获取事件详情失败:', error);
      // 如果出错，使用原始事件
      setSelectedEvent(event);
      
      // 只设置描述和结果字段
      const formValues = {
        description: event.description,
        outcome: event.outcome
      };
      
      editForm.setFieldsValue(formValues);
      setShowEditModal(true);
    }
  };

  // 编辑事件提交
  const handleEditEvent = async (values: any) => {
    if (!selectedEvent) {
      message.error('没有选中要编辑的事件');
      return;
    }
    
    try {
      setLoading(true);
      
      // 只处理描述和结果字段
      const processedValues = {
        description: values.description,
        outcome: values.outcome
      };
      
      console.log('发送编辑数据:', processedValues);
      
      const response = await fetch(`http://localhost:8001/api/v1/events/${selectedEvent.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(processedValues),
      });

      if (response.ok) {
        message.success('事件更新成功');
        setShowEditModal(false);
        await fetchEventsWithScores();
      } else {
        const errorData = await response.json();
        message.error(errorData.detail || '更新失败');
      }
    } catch (error) {
      console.error('更新事件失败:', error);
      message.error('更新失败');
    } finally {
      setLoading(false);
    }
  };

  // 批量删除事件
  const handleBatchDelete = async (eventIds: string[]) => {
    setLoading(true);
    try {
      const promises = eventIds.map(id => 
        fetch(`http://localhost:8001/api/v1/events/${id}`, { method: 'DELETE' })
      );
      await Promise.all(promises);
      message.success(`成功删除${eventIds.length}个事件`);
      await fetchEventsWithScores();
    } catch (error) {
      message.error('批量删除失败');
    } finally {
      setLoading(false);
    }
  };

  // ==================== 事件评分与进化相关函数 ====================
  
  // 对事件进行评分
  const handleScoreEvent = async (eventId: string) => {
    setScoringLoading(eventId); // 设置当前正在评分的事件ID
    try {
      const response = await fetch(`http://localhost:8001/api/v1/events/${eventId}/score`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        setCurrentScore(data.score);
        setShowScoreModal(true);
        message.success('事件评分完成');
        // 刷新事件列表以显示最新评分
        await fetchEventsWithScores();
      } else {
        const errorData = await response.json();
        message.error(errorData.detail || '评分失败');
      }
    } catch (error) {
      console.error('评分失败:', error);
      message.error('评分失败');
    } finally {
      setScoringLoading(null); // 清除loading状态
    }
  };
  
  // 获取事件的最新评分并显示进化确认弹窗
  const handleGetLatestScore = async (eventId: string) => {
    try {
      const response = await fetch(`http://localhost:8001/api/v1/events/${eventId}/latest-score`);
      
      if (response.ok) {
        const data = await response.json();
        if (data.success && data.score) {
          setCurrentScore(data.score);
          setPendingEvolutionEventId(eventId);
          setShowEvolutionConfirmModal(true);
        } else {
          message.info('该事件暂无评分记录，无法进行进化');
        }
      } else {
        const errorData = await response.json();
        message.error(errorData.detail || '获取评分失败');
      }
    } catch (error) {
      console.error('获取评分失败:', error);
      message.error('获取评分失败');
    }
  };
  
  // 确认进化事件
  const handleConfirmEvolution = async () => {
    if (!pendingEvolutionEventId || !currentScore) {
      message.error('缺少必要信息，无法进行进化');
      return;
    }
    
    setShowEvolutionConfirmModal(false);
    
    // 获取最新评分的ID
    try {
      const response = await fetch(`http://localhost:8001/api/v1/events/${pendingEvolutionEventId}/latest-score`);
      if (response.ok) {
        const data = await response.json();
        if (data.success && data.score) {
          // 使用最新评分的ID进行进化，传递自定义描述
          await handleEvolveEvent(pendingEvolutionEventId, data.score.id, customEvolutionDescription);
          setCustomEvolutionDescription(''); // 清空自定义描述
        } else {
          message.error('无法获取最新评分ID');
        }
      } else {
        message.error('获取最新评分失败');
      }
    } catch (error) {
      console.error('获取最新评分失败:', error);
      message.error('获取最新评分失败');
    }
    
    setPendingEvolutionEventId(null);
  };

  // 进化事件
  const handleEvolveEvent = async (eventId: string, scoreId: number, customDescription: string = '') => {
    setEvolutionLoading(eventId); // 设置当前正在进化的事件ID
    try {
      // 先获取原始事件信息
      const eventResponse = await fetch(`http://localhost:8001/api/v1/events/${eventId}`);
      if (eventResponse.ok) {
        const eventData = await eventResponse.json();
        setSelectedEvent(eventData); // 设置原始事件
      }
      
      const response = await fetch(`http://localhost:8001/api/v1/events/${eventId}/evolve?score_id=${scoreId}&custom_description=${encodeURIComponent(customDescription)}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        setEvolvedEvent(data.evolved_event); // 存储进化后的事件
        setShowEvolutionModal(true);
        message.success('事件进化完成');
        // 刷新事件列表以显示最新状态
        await fetchEventsWithScores();
      } else {
        const errorData = await response.json();
        message.error(errorData.detail || '进化失败');
      }
    } catch (error) {
      console.error('进化失败:', error);
      message.error('进化失败');
    } finally {
      setEvolutionLoading(null); // 清除loading状态
    }
  };
  
  // 获取事件进化历史
  const handleGetEvolutionHistory = async (eventId: string) => {
    try {
      const response = await fetch(`http://localhost:8001/api/v1/events/${eventId}/evolution-history`);
      
      if (response.ok) {
        const data = await response.json();
        setCurrentEvolutionHistory(data.history);
        setShowEvolutionHistoryModal(true);
      } else {
        const errorData = await response.json();
        message.error(errorData.detail || '获取进化历史失败');
      }
    } catch (error) {
      console.error('获取进化历史失败:', error);
      message.error('获取进化历史失败');
    }
  };
  
  // 获取事件详情（优先显示最新进化内容）
  const fetchEventDetail = async (eventId: string) => {
    try {
      const response = await fetch(`http://localhost:8001/api/v1/events/${eventId}/detail`);
      if (response.ok) {
        const data = await response.json();
        setEventDetail(data);
        setShowEventDetailModal(true);
      } else {
        message.error('获取事件详情失败');
      }
    } catch (error) {
      console.error('获取事件详情失败:', error);
      message.error('获取事件详情失败');
    }
  };

  // 获取进化历史（用于对比展示）
  const fetchEvolutionHistory = async (eventId: string) => {
    try {
      const response = await fetch(`http://localhost:8001/api/v1/events/${eventId}/evolution-history`);
      if (response.ok) {
        const data = await response.json();
        setEvolutionHistory(data);
        setShowEvolutionCompareModal(true);
      } else {
        message.error('获取进化历史失败');
      }
    } catch (error) {
      console.error('获取进化历史失败:', error);
      message.error('获取进化历史失败');
    }
  };

  // 获取事件统计
  const getEventStatistics = () => {
    if (!events.length) return {};

    const stats = {
      total: events.length,
      byType: {} as Record<string, number>
    };

    // 统计类型分布
    events.forEach(event => {
      stats.byType[event.event_type] = (stats.byType[event.event_type] || 0) + 1;
    });

    return stats;
  };

  // 过滤事件
  const filteredEvents = events.filter(event => {
    const matchesSearch = !searchText || 
      event.title.toLowerCase().includes(searchText.toLowerCase()) ||
      event.description.toLowerCase().includes(searchText.toLowerCase());
    
    const matchesType = !filterType || event.event_type === filterType;
    const matchesImportance = !filterImportance || event.importance === filterImportance;
    const matchesPlot = !selectedPlotOutline || event.plot_outline_id === selectedPlotOutline;
    
    return matchesSearch && matchesType && matchesImportance && matchesPlot;
  });

  // 表格列定义
  const columns = [
    {
      title: '序号',
      dataIndex: 'sequence_order',
      key: 'sequence_order',
      width: 60,
      sorter: (a: Event, b: Event) => a.sequence_order - b.sequence_order,
    },
    {
      title: '事件标题',
      dataIndex: 'title',
      key: 'title',
      width: 180,
      ellipsis: true,
      render: (text: string, record: Event) => (
        <div>
          <Button type="link" onClick={() => handleViewEvent(record)} style={{ textAlign: 'left', padding: 0 }}>
            {text}
          </Button>
          {record.version && record.version > 1 && (
            <Tag size="small" color="blue" style={{ marginLeft: 4 }}>
              v{record.version}
            </Tag>
          )}
        </div>
      ),
    },
    {
      title: '类型',
      dataIndex: 'event_type',
      key: 'event_type',
      width: 80,
      render: (type: string) => {
        const colors: Record<string, string> = {
          '重大事件': 'red',
          '冲突事件': 'volcano',
          '特殊事件': 'purple',
          '日常事件': 'blue',
        };
        return <Tag color={colors[type] || 'default'}>{type}</Tag>;
      },
    },
    {
      title: '综合评分',
      key: 'overall_score',
      width: 100,
      render: (_, record: Event & { latest_score?: EventScore }) => {
        if (record.latest_score) {
          const score = record.latest_score.overall_quality;
          const color = score >= 8 ? '#52c41a' : score >= 6 ? '#faad14' : '#ff4d4f';
          return (
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '16px', fontWeight: 'bold', color }}>{score.toFixed(1)}</div>
              <div style={{ fontSize: '10px', color: '#999' }}>/10</div>
            </div>
          );
        }
        return <Text type="secondary">未评分</Text>;
      },
    },
    {
      title: '文笔质量',
      key: 'writing_score',
      width: 80,
      render: (_, record: Event & { latest_score?: EventScore }) => {
        if (record.latest_score) {
          const score = record.latest_score.writing_quality;
          const color = score >= 8 ? '#52c41a' : score >= 6 ? '#faad14' : '#ff4d4f';
          return (
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '14px', fontWeight: 'bold', color }}>{score.toFixed(1)}</div>
              <div style={{ fontSize: '10px', color: '#999' }}>/10</div>
            </div>
          );
        }
        return <Text type="secondary">-</Text>;
      },
    },
    {
      title: '章节',
      dataIndex: 'chapter_number',
      key: 'chapter_number',
      width: 60,
      render: (chapterNumber: number) => chapterNumber ? `第${chapterNumber}章` : '-',
    },
    {
      title: '操作',
      key: 'actions',
      width: 160,
      render: (_, record: Event) => (
        <Space size="small">
          <Tooltip title="查看详情">
            <Button
              type="text"
              size="small"
              icon={<EyeOutlined />}
              onClick={() => handleViewEventDrawer(record)}
            />
          </Tooltip>
          <Tooltip title="编辑">
            <Button
              type="text"
              size="small"
              icon={<EditOutlined />}
              onClick={() => handleEdit(record)}
            />
          </Tooltip>
          <Tooltip title="评分">
            <Button
              type="text"
              size="small"
              icon={<TrophyOutlined />}
              loading={scoringLoading === record.id}
              onClick={() => handleScoreEvent(record.id)}
            />
          </Tooltip>
          <Tooltip title="进化">
            <Button
              type="text"
              size="small"
              icon={<SyncOutlined />}
              loading={evolutionLoading === record.id}
              onClick={() => handleGetLatestScore(record.id)}
            />
          </Tooltip>
          <Tooltip title="进化对比">
            <Button
              type="text"
              size="small"
              icon={<DiffOutlined />}
              onClick={() => fetchEvolutionHistory(record.id)}
            />
          </Tooltip>
          <Popconfirm
            title="确定要删除这个事件吗？"
            onConfirm={() => handleDeleteEvent(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Tooltip title="删除">
              <Button
                type="text"
                size="small"
                danger
                icon={<DeleteOutlined />}
              />
            </Tooltip>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  useEffect(() => {
    fetchEventsWithScores();
    fetchPlotOutlines();
    fetchWorldViews();
  }, []);

  const stats = getEventStatistics();

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <Title level={2}>
          <CalendarOutlined style={{ marginRight: 8 }} />
          事件管理
        </Title>
        <Text type="secondary" style={{ fontSize: 16 }}>
          生成、管理和查看小说中的事件，支持批量操作和统计分析。
        </Text>
      </div>

      {/* 生成按钮 */}
      <Card style={{ marginBottom: 24 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <Title level={3} style={{ margin: 0 }}>
              <CalendarOutlined style={{ marginRight: 8 }} />
              生成事件
            </Title>
            <Text type="secondary">
              智能分级生成事件，支持重要性分布和章节融入
            </Text>
          </div>
          <Button
            type="primary"
            size="large"
            icon={<PlayCircleOutlined />}
            onClick={() => setShowGenerateModal(true)}
            style={{ height: 50, fontSize: 16, marginRight: 16 }}
          >
            生成事件
          </Button>
        </div>
      </Card>

      {/* 统计信息 */}
      {events.length > 0 && (
        <Row gutter={16} style={{ marginBottom: 24 }}>
          <Col span={6}>
            <Card>
              <Statistic title="总事件数" value={stats.total || 0} />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic title="已筛选" value={filteredEvents.length} />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic 
                title="已分配章节" 
                value={events.filter(e => e.chapter_number).length} 
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic 
                title="今日新增" 
                value={events.filter(e => {
                  const today = new Date().toDateString();
                  return new Date(e.created_at).toDateString() === today;
                }).length} 
              />
            </Card>
          </Col>
        </Row>
      )}

      <Card>
        <Tabs activeKey={activeTab} onChange={setActiveTab}>
          <TabPane tab="事件列表" key="list">
            {/* 筛选和控制区 */}
            <Row gutter={16} style={{ marginBottom: 16 }}>
              <Col span={6}>
                <Select
                  placeholder="按剧情大纲筛选"
                  value={selectedPlotOutline}
                  onChange={(value) => {
                    setSelectedPlotOutline(value);
                    fetchEventsWithScores();
                  }}
                  allowClear
                  style={{ width: '100%' }}
                >
                  {plotOutlines.map((plot: any) => (
                    <Option key={plot.id} value={plot.id}>
                      {plot.title}
                    </Option>
                  ))}
                </Select>
              </Col>
              <Col span={6}>
                <Input
                  placeholder="搜索事件标题或描述"
                  prefix={<SearchOutlined />}
                  value={searchText}
                  onChange={(e) => setSearchText(e.target.value)}
                  allowClear
                />
              </Col>
              <Col span={6}>
                <Select
                  placeholder="按类型筛选"
                  value={filterType}
                  onChange={setFilterType}
                  allowClear
                  style={{ width: '100%' }}
                >
                  {eventTypes.map(type => (
                    <Option key={type} value={type}>{type}</Option>
                  ))}
                </Select>
              </Col>
              <Col span={6}>
                <Space>
                  <Button
                    icon={<ReloadOutlined />}
                    onClick={() => fetchEventsWithScores()}
                  >
                    刷新
                  </Button>
                  <Button
                    icon={<BarChartOutlined />}
                    onClick={() => setShowStatsModal(true)}
                  >
                    统计
                  </Button>
                  {selectedRowKeys.length > 0 && (
                    <Popconfirm
                      title={`确定要删除选中的${selectedRowKeys.length}个事件吗？`}
                      onConfirm={() => handleBatchDelete(selectedRowKeys as string[])}
                      okText="确定"
                      cancelText="取消"
                    >
                      <Button
                        danger
                        icon={<DeleteOutlined />}
                      >
                        批量删除 ({selectedRowKeys.length})
                      </Button>
                    </Popconfirm>
                  )}
                </Space>
              </Col>
            </Row>

            {events.length === 0 ? (
              <Empty 
                description="暂无事件，请先生成事件"
                image={Empty.PRESENTED_IMAGE_SIMPLE}
              />
            ) : (
              <Table
              columns={columns}
              dataSource={filteredEvents}
              rowKey="id"
              loading={loading}
              pagination={{
                pageSize: 10,
                showSizeChanger: true,
                showQuickJumper: true,
                showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条，共 ${total} 条`,
              }}
              scroll={{ x: 1000 }}
              rowSelection={{
                selectedRowKeys,
                onChange: (selectedRowKeys, selectedRows) => {
                  setSelectedRowKeys(selectedRowKeys);
                  setSelectedEvents(selectedRows);
                },
                getCheckboxProps: (record) => ({
                  name: record.title,
                }),
              }}
            />
            )}
          </TabPane>

          <TabPane tab="统计分析" key="stats">
            <Row gutter={16}>
              <Col span={12}>
                <Card title="类型分布" style={{ marginBottom: 16 }}>
                  {Object.entries(stats.byType || {}).map(([type, count]) => (
                    <div key={type} style={{ marginBottom: 8 }}>
                      <Space>
                        <Text>{type}</Text>
                        <Badge count={count} showZero />
                        <Progress 
                          percent={Math.round((count as number) / (stats.total || 1) * 100)} 
                          style={{ width: 200 }}
                          size="small"
                        />
                      </Space>
                    </div>
                  ))}
                </Card>
              </Col>
            </Row>

            <Row gutter={16}>
              <Col span={12}>
                <Card title="章节分布" style={{ marginBottom: 16 }}>
                  {events.filter(e => e.chapter_number).length > 0 ? (
                    <div>
                      {Array.from(new Set(events.filter(e => e.chapter_number).map(e => e.chapter_number)))
                        .sort((a, b) => a - b)
                        .map(chapter => {
                          const count = events.filter(e => e.chapter_number === chapter).length;
                          return (
                            <div key={chapter} style={{ marginBottom: 8 }}>
                              <Space>
                                <Text>第{chapter}章</Text>
                                <Badge count={count} showZero />
                                <Progress 
                                  percent={Math.round(count / (stats.total || 1) * 100)} 
                                  style={{ width: 200 }}
                                  size="small"
                                />
                              </Space>
                            </div>
                          );
                        })}
                    </div>
                  ) : (
                    <Text type="secondary">暂无已分配章节的事件</Text>
                  )}
                </Card>
              </Col>
              <Col span={12}>
                <Card title="时间分布" style={{ marginBottom: 16 }}>
                  <div style={{ marginBottom: 8 }}>
                    <Text>今日新增: </Text>
                    <Tag color="blue">
                      {events.filter(e => {
                        const today = new Date().toDateString();
                        return new Date(e.created_at).toDateString() === today;
                      }).length}
                    </Tag>
                  </div>
                  <div style={{ marginBottom: 8 }}>
                    <Text>本周新增: </Text>
                    <Tag color="green">
                      {events.filter(e => {
                        const weekAgo = new Date();
                        weekAgo.setDate(weekAgo.getDate() - 7);
                        return new Date(e.created_at) >= weekAgo;
                      }).length}
                    </Tag>
                  </div>
                </Card>
              </Col>
            </Row>
          </TabPane>
        </Tabs>
      </Card>

      {/* 生成事件模态框 */}
      <Modal
        title="生成事件"
        open={showGenerateModal}
        onCancel={() => setShowGenerateModal(false)}
        footer={null}
        width={800}
      >
        <Form
          form={generateForm}
          layout="vertical"
          onFinish={handleGenerateEvents}
        >
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="worldview_id"
                label="选择世界观"
              >
                <Select 
                  placeholder="请选择世界观（可选）" 
                  value={selectedWorldView}
                  onChange={(value) => {
                    setSelectedWorldView(value);
                    if (value) {
                      fetchCharacters(value);
                    }
                  }}
                  allowClear
                >
                  {worldViews.map((world: any) => (
                    <Option key={world.worldview_id} value={world.worldview_id}>
                      {world.name}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="plot_outline_id"
                label="选择剧情大纲"
                rules={[{ required: true, message: '请选择剧情大纲' }]}
              >
                <Select 
                  placeholder="请选择剧情大纲（必选）" 
                  value={selectedPlotOutline}
                  onChange={(value) => {
                    setSelectedPlotOutline(value);
                    if (value) {
                      fetchPlotActs(value);
                    } else {
                      setPlotActs(null);
                      setSelectedAct(null);
                    }
                  }}
                  allowClear
                >
                  {plotOutlines.map((plot: any) => (
                    <Option key={plot.id} value={plot.id}>
                      {plot.title}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
          </Row>

          {/* 幕次选择 */}
          {plotActs && plotActs.acts.length > 0 && (
            <>
              <Divider>幕次选择（可选）</Divider>
              <Form.Item label="选择幕次">
                <Select
                  placeholder="请选择要生成事件的幕次（可选，不选择则生成所有幕次的事件）"
                  value={selectedAct ? selectedAct.act_number : undefined}
                  onChange={(value) => {
                    const act = plotActs.acts.find(a => a.act_number === value);
                    setSelectedAct(act || null);
                  }}
                  allowClear
                >
                  {plotActs.acts.map((act) => (
                    <Option key={act.act_number} value={act.act_number}>
                      {act.act_name} - {act.core_mission}
                    </Option>
                  ))}
                </Select>
                {selectedAct && (
                  <div style={{ marginTop: 8, padding: 12, background: '#f5f5f5', borderRadius: 4 }}>
                    <Text strong>选中幕次详情：</Text>
                    <div style={{ marginTop: 4 }}>
                      <Text type="secondary">核心任务：{selectedAct.core_mission}</Text>
                    </div>
                    <div style={{ marginTop: 4 }}>
                      <Text type="secondary">日常事件：{selectedAct.daily_events}</Text>
                    </div>
                    <div style={{ marginTop: 4 }}>
                      <Text type="secondary">冲突事件：{selectedAct.conflict_events}</Text>
                    </div>
                    <div style={{ marginTop: 4 }}>
                      <Text type="secondary">特殊事件：{selectedAct.special_events}</Text>
                    </div>
                    <div style={{ marginTop: 4 }}>
                      <Text type="secondary">重大事件：{selectedAct.major_events}</Text>
                    </div>
                  </div>
                )}
              </Form.Item>
            </>
          )}

          {/* 重要性分布配置 */}
          <Divider>重要性分布配置</Divider>
              
              {/* 重要性分布配置 */}
              <Card title="重要性分布" size="small" style={{ marginBottom: 16 }}>
                <Row gutter={16}>
                  <Col span={12}>
                    <div style={{ marginBottom: 16 }}>
                      <Text strong>重大事件</Text>
                      <Slider
                        min={0}
                        max={10}
                        value={importanceDistribution.major}
                        onChange={(value) => setImportanceDistribution(prev => ({ ...prev, major: value }))}
                        marks={{ 0: '0', 5: '5', 10: '10' }}
                      />
                      <Text type="secondary">推动主线剧情的关键事件</Text>
                    </div>
                    <div style={{ marginBottom: 16 }}>
                      <Text strong>冲突事件</Text>
                      <Slider
                        min={0}
                        max={15}
                        value={importanceDistribution.conflict}
                        onChange={(value) => setImportanceDistribution(prev => ({ ...prev, conflict: value }))}
                        marks={{ 0: '0', 7: '7', 15: '15' }}
                      />
                      <Text type="secondary">发展角色关系的冲突事件</Text>
                    </div>
                  </Col>
                  <Col span={12}>
                    <div style={{ marginBottom: 16 }}>
                      <Text strong>日常事件</Text>
                      <Slider
                        min={0}
                        max={20}
                        value={importanceDistribution.daily}
                        onChange={(value) => setImportanceDistribution(prev => ({ ...prev, daily: value }))}
                        marks={{ 0: '0', 10: '10', 20: '20' }}
                      />
                      <Text type="secondary">丰富世界观细节的日常事件</Text>
                    </div>
                    <div style={{ marginBottom: 16 }}>
                      <Text strong>特殊事件</Text>
                      <Slider
                        min={0}
                        max={8}
                        value={importanceDistribution.special}
                        onChange={(value) => setImportanceDistribution(prev => ({ ...prev, special: value }))}
                        marks={{ 0: '0', 4: '4', 8: '8' }}
                      />
                      <Text type="secondary">增加故事趣味性的特殊事件</Text>
                    </div>
                  </Col>
                </Row>
                <Alert
                  message={`总计将生成 ${importanceDistribution.major + importanceDistribution.conflict + importanceDistribution.daily + importanceDistribution.special} 个事件`}
                  type="info"
                  showIcon
                  style={{ marginTop: 16 }}
                />
              </Card>

              {/* 自动角色分配说明 */}
              <Alert
                message="角色自动分配"
                description="系统将根据事件类型和剧情需要自动选择合适的角色参与事件，无需手动选择"
                type="info"
                showIcon
                style={{ marginBottom: 16 }}
              />

              {/* 章节融入配置 */}
              <Form.Item label="章节融入">
                <Space>
                  <Switch
                    checked={true}
                    disabled
                  />
                  <Text>生成章节融入信息</Text>
                </Space>
                <Text type="secondary" style={{ display: 'block', marginTop: 4 }}>
                  为每个事件生成故事位置、核心矛盾、戏剧张力等信息，便于后续章节大纲生成
                </Text>
              </Form.Item>


          <Form.Item
            name="event_requirements"
            label="事件要求"
            rules={[{ required: true, message: '请输入事件要求' }]}
            initialValue=""
          >
            <TextArea
              rows={3}
              placeholder="请描述要生成的事件类型和要求"
            />
          </Form.Item>

          <Form.Item style={{ marginBottom: 0, textAlign: 'right' }}>
            <Space>
              <Button onClick={() => setShowGenerateModal(false)}>
                取消
              </Button>
              <Button type="primary" htmlType="submit" loading={loading}>
                生成事件
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* 事件详情模态框 */}
      <Modal
        title="事件详情"
        open={showDetailModal}
        onCancel={() => setShowDetailModal(false)}
        footer={[
          <Button key="close" onClick={() => setShowDetailModal(false)}>
            关闭
          </Button>
        ]}
        width={800}
      >
        {selectedEvent && (
          <div>
            <Descriptions column={2} bordered>
              <Descriptions.Item label="事件标题" span={2}>
                <Title level={4} style={{ margin: 0 }}>{selectedEvent.title}</Title>
              </Descriptions.Item>
              <Descriptions.Item label="事件类型">
                <Tag color="blue" style={{ fontSize: 14, padding: '4px 8px' }}>
                  {selectedEvent.event_type}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="章节">
                {selectedEvent.chapter_number ? `第${selectedEvent.chapter_number}章` : '未分配'}
              </Descriptions.Item>
              <Descriptions.Item label="序号">
                {selectedEvent.sequence_order || 0}
              </Descriptions.Item>
              <Descriptions.Item label="创建时间">
                {new Date(selectedEvent.created_at).toLocaleString()}
              </Descriptions.Item>
              <Descriptions.Item label="更新时间">
                {selectedEvent.updated_at ? new Date(selectedEvent.updated_at).toLocaleString() : '-'}
              </Descriptions.Item>
            </Descriptions>

            <Divider />
            <Title level={4}>事件描述</Title>
            <div style={{ 
              padding: 16, 
              background: '#fafafa', 
              borderRadius: 6, 
              border: '1px solid #d9d9d9',
              lineHeight: '1.6',
              fontSize: 14
            }}>
              {selectedEvent.description}
            </div>

            <Divider />
            <Title level={4}>事件结果</Title>
            <div style={{ 
              padding: 16, 
              background: '#f6ffed', 
              borderRadius: 6, 
              border: '1px solid #b7eb8f',
              lineHeight: '1.6',
              fontSize: 14
            }}>
              {selectedEvent.outcome}
            </div>


          </div>
        )}
      </Modal>

      {/* 事件详情抽屉 */}
      <Drawer
        title={selectedEvent?.title || '事件详情'}
        open={showDetailDrawer}
        onClose={() => setShowDetailDrawer(false)}
        width={600}
        extra={
          <Space>
            <Button icon={<EditOutlined />} onClick={() => {
              setShowDetailDrawer(false);
              handleEdit(selectedEvent!);
            }}>
              编辑
            </Button>
          </Space>
        }
      >
        {selectedEvent && (
          <div>
            <Descriptions column={1} bordered>
              <Descriptions.Item label="事件类型">
                <Tag color="blue" style={{ fontSize: 14, padding: '4px 8px' }}>
                  {selectedEvent.event_type}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="章节">
                {selectedEvent.chapter_number ? `第${selectedEvent.chapter_number}章` : '未分配'}
              </Descriptions.Item>
              <Descriptions.Item label="序号">
                {selectedEvent.sequence_order || 0}
              </Descriptions.Item>
              <Descriptions.Item label="创建时间">
                {new Date(selectedEvent.created_at).toLocaleString()}
              </Descriptions.Item>
            </Descriptions>

            <Divider />
            <Title level={4}>事件描述</Title>
            <div style={{ 
              padding: 16, 
              background: '#fafafa', 
              borderRadius: 6, 
              border: '1px solid #d9d9d9',
              lineHeight: '1.6',
              fontSize: 14
            }}>
              {selectedEvent.description}
            </div>

            <Divider />
            <Title level={4}>事件结果</Title>
            <div style={{ 
              padding: 16, 
              background: '#f6ffed', 
              borderRadius: 6, 
              border: '1px solid #b7eb8f',
              lineHeight: '1.6',
              fontSize: 14
            }}>
              {selectedEvent.outcome}
            </div>

          </div>
        )}
      </Drawer>

      {/* 编辑事件模态框 */}
      <Modal
        title="编辑事件"
        open={showEditModal}
        onCancel={() => setShowEditModal(false)}
        footer={null}
        width={600}
      >
        <Form
          form={editForm}
          onFinish={handleEditEvent}
          layout="vertical"
        >
          <Form.Item 
            label="事件描述"
            name="description"
            rules={[{ required: true, message: '请输入事件描述' }]}
          >
            <TextArea 
              rows={8} 
              placeholder="详细描述事件的经过、参与角色、环境等"
              showCount
              maxLength={2000}
            />
          </Form.Item>

          <Form.Item 
            label="事件结果"
            name="outcome"
            rules={[{ required: true, message: '请输入事件结果' }]}
          >
            <TextArea 
              rows={8} 
              placeholder="描述事件的结果、影响、后续发展等"
              showCount
              maxLength={2000}
            />
          </Form.Item>

          <Form.Item style={{ marginBottom: 0, textAlign: 'right' }}>
            <Space>
              <Button onClick={() => setShowEditModal(false)}>
                取消
              </Button>
              <Button type="primary" htmlType="submit" loading={loading}>
                保存修改
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* 事件评分模态框 */}
      <Modal
        title="事件评分结果"
        open={showScoreModal}
        onCancel={() => setShowScoreModal(false)}
        footer={[
          <Button key="close" onClick={() => setShowScoreModal(false)}>
            关闭
          </Button>
        ]}
        width={800}
      >
        {currentScore && (
          <div>
            <Row gutter={16} style={{ marginBottom: 24 }}>
              <Col span={6}>
                <Statistic 
                  title="主角参与度" 
                  value={currentScore.protagonist_involvement} 
                  suffix="/10"
                  valueStyle={{ color: currentScore.protagonist_involvement >= 7 ? '#3f8600' : '#cf1322' }}
                />
              </Col>
              <Col span={6}>
                <Statistic 
                  title="剧情逻辑性" 
                  value={currentScore.plot_coherence} 
                  suffix="/10"
                  valueStyle={{ color: currentScore.plot_coherence >= 7 ? '#3f8600' : '#cf1322' }}
                />
              </Col>
              <Col span={6}>
                <Statistic 
                  title="文笔质量" 
                  value={currentScore.writing_quality} 
                  suffix="/10"
                  valueStyle={{ color: currentScore.writing_quality >= 7 ? '#3f8600' : '#cf1322' }}
                />
              </Col>
              <Col span={6}>
                <Statistic 
                  title="综合质量" 
                  value={currentScore.overall_quality} 
                  suffix="/10"
                  valueStyle={{ color: currentScore.overall_quality >= 7 ? '#3f8600' : '#cf1322' }}
                />
              </Col>
            </Row>
            
            <Row gutter={16} style={{ marginBottom: 24 }}>
              <Col span={6}>
                <Statistic 
                  title="戏剧张力" 
                  value={currentScore.dramatic_tension} 
                  suffix="/10"
                  valueStyle={{ color: currentScore.dramatic_tension >= 7 ? '#3f8600' : '#cf1322' }}
                />
              </Col>
            </Row>

            <Divider />
            
            <div style={{ marginBottom: 16 }}>
              <Title level={5}>改进建议</Title>
              <Text>{currentScore.feedback}</Text>
            </div>

            <Row gutter={16}>
              <Col span={12}>
                <Title level={5}>优点</Title>
                <List
                  size="small"
                  dataSource={currentScore.strengths}
                  renderItem={(item) => (
                    <List.Item>
                      <Text type="success">✓ {item}</Text>
                    </List.Item>
                  )}
                />
              </Col>
              <Col span={12}>
                <Title level={5}>缺点</Title>
                <List
                  size="small"
                  dataSource={currentScore.weaknesses}
                  renderItem={(item) => (
                    <List.Item>
                      <Text type="danger">✗ {item}</Text>
                    </List.Item>
                  )}
                />
              </Col>
            </Row>
          </div>
        )}
      </Modal>

      {/* 进化确认模态框 */}
      <Modal
        title="事件进化确认"
        open={showEvolutionConfirmModal}
        onCancel={() => {
          setShowEvolutionConfirmModal(false);
          setPendingEvolutionEventId(null);
        }}
        footer={[
          <Button key="cancel" onClick={() => {
            setShowEvolutionConfirmModal(false);
            setPendingEvolutionEventId(null);
          }}>
            取消
          </Button>,
          <Button 
            key="confirm" 
            type="primary" 
            icon={<SyncOutlined />}
            onClick={handleConfirmEvolution}
          >
            确认进化
          </Button>
        ]}
        width={800}
      >
        {currentScore && (
          <div>
            <Alert
              message="基于评分维度进行事件进化"
              description="系统将根据以下评分维度对事件进行优化，提升事件质量。"
              type="info"
              showIcon
              style={{ marginBottom: 24 }}
            />
            
            <Title level={4} style={{ marginBottom: 16 }}>当前评分维度</Title>
            
            <Row gutter={16} style={{ marginBottom: 24 }}>
              <Col span={8}>
                <Card size="small" style={{ textAlign: 'center' }}>
                  <Statistic 
                    title="主角参与度" 
                    value={currentScore.protagonist_involvement} 
                    suffix="/10"
                    valueStyle={{ 
                      color: currentScore.protagonist_involvement >= 8 ? '#52c41a' : 
                             currentScore.protagonist_involvement >= 6 ? '#faad14' : '#ff4d4f',
                      fontSize: '18px'
                    }}
                  />
                  <Text type="secondary" style={{ fontSize: '12px' }}>
                    {currentScore.protagonist_involvement >= 8 ? '优秀' : 
                     currentScore.protagonist_involvement >= 6 ? '良好' : '需改进'}
                  </Text>
                </Card>
              </Col>
              <Col span={8}>
                <Card size="small" style={{ textAlign: 'center' }}>
                  <Statistic 
                    title="剧情逻辑性" 
                    value={currentScore.plot_coherence} 
                    suffix="/10"
                    valueStyle={{ 
                      color: currentScore.plot_coherence >= 8 ? '#52c41a' : 
                             currentScore.plot_coherence >= 6 ? '#faad14' : '#ff4d4f',
                      fontSize: '18px'
                    }}
                  />
                  <Text type="secondary" style={{ fontSize: '12px' }}>
                    {currentScore.plot_coherence >= 8 ? '优秀' : 
                     currentScore.plot_coherence >= 6 ? '良好' : '需改进'}
                  </Text>
                </Card>
              </Col>
              <Col span={8}>
                <Card size="small" style={{ textAlign: 'center' }}>
                  <Statistic 
                    title="文笔质量" 
                    value={currentScore.writing_quality} 
                    suffix="/10"
                    valueStyle={{ 
                      color: currentScore.writing_quality >= 8 ? '#52c41a' : 
                             currentScore.writing_quality >= 6 ? '#faad14' : '#ff4d4f',
                      fontSize: '18px'
                    }}
                  />
                  <Text type="secondary" style={{ fontSize: '12px' }}>
                    {currentScore.writing_quality >= 8 ? '优秀' : 
                     currentScore.writing_quality >= 6 ? '良好' : '需改进'}
                  </Text>
                </Card>
              </Col>
            </Row>
            
            <Row gutter={16} style={{ marginBottom: 24 }}>
              <Col span={12}>
                <Card size="small" style={{ textAlign: 'center' }}>
                  <Statistic 
                    title="戏剧张力" 
                    value={currentScore.dramatic_tension} 
                    suffix="/10"
                    valueStyle={{ 
                      color: currentScore.dramatic_tension >= 8 ? '#52c41a' : 
                             currentScore.dramatic_tension >= 6 ? '#faad14' : '#ff4d4f',
                      fontSize: '18px'
                    }}
                  />
                  <Text type="secondary" style={{ fontSize: '12px' }}>
                    {currentScore.dramatic_tension >= 8 ? '优秀' : 
                     currentScore.dramatic_tension >= 6 ? '良好' : '需改进'}
                  </Text>
                </Card>
              </Col>
              <Col span={12}>
                <Card size="small" style={{ textAlign: 'center' }}>
                  <Statistic 
                    title="综合质量" 
                    value={currentScore.overall_quality} 
                    suffix="/10"
                    valueStyle={{ 
                      color: currentScore.overall_quality >= 8 ? '#52c41a' : 
                             currentScore.overall_quality >= 6 ? '#faad14' : '#ff4d4f',
                      fontSize: '18px'
                    }}
                  />
                  <Text type="secondary" style={{ fontSize: '12px' }}>
                    {currentScore.overall_quality >= 8 ? '优秀' : 
                     currentScore.overall_quality >= 6 ? '良好' : '需改进'}
                  </Text>
                </Card>
              </Col>
            </Row>

            <Divider />
            
            <div style={{ marginBottom: 16 }}>
              <Title level={5}>进化策略</Title>
              <Text>
                系统将根据评分结果，重点优化得分较低的维度：
                {currentScore.protagonist_involvement < 7 && ' 增强主角参与度'}
                {currentScore.plot_coherence < 7 && ' 提升剧情逻辑性'}
                {currentScore.writing_quality < 7 && ' 改善文笔质量'}
                {currentScore.dramatic_tension < 7 && ' 增强戏剧张力'}
                {currentScore.overall_quality < 7 && ' 全面提升质量'}
              </Text>
            </div>

            <div style={{ marginBottom: 16 }}>
              <Title level={5}>改进建议</Title>
              <Text>{currentScore.feedback}</Text>
            </div>

            <Divider />
            
            <div style={{ marginBottom: 16 }}>
              <Title level={5}>自定义进化要求（可选）</Title>
              <TextArea
                rows={4}
                placeholder="请输入您对事件进化的特殊要求，例如：增加更多心理描写、强化某个角色的作用、调整事件节奏等..."
                value={customEvolutionDescription}
                onChange={(e) => setCustomEvolutionDescription(e.target.value)}
                style={{ marginTop: 8 }}
              />
              <Text type="secondary" style={{ fontSize: '12px' }}>
                如果不填写，系统将按照评分结果进行标准优化
              </Text>
            </div>
          </div>
        )}
      </Modal>

      {/* 事件进化模态框 */}
      <Modal
        title="事件进化结果"
        open={showEvolutionModal}
        onCancel={() => setShowEvolutionModal(false)}
        footer={[
          <Button key="close" onClick={() => setShowEvolutionModal(false)}>
            关闭
          </Button>
        ]}
        width={1200}
      >
        <div>
          <Alert
            message="事件进化完成"
            description="基于评分结果，系统已对事件进行了优化。进化版本已自动保存，您可以查看对比结果。"
            type="success"
            showIcon
            style={{ marginBottom: 16 }}
          />
          
          <Row gutter={16}>
            <Col span={12}>
              <Card title="原始事件" size="small">
                <div>
                  <Title level={5}>{selectedEvent?.title}</Title>
                  <Text>{selectedEvent?.description}</Text>
                  <Divider />
                  <Title level={5}>事件结果</Title>
                  <Text>{selectedEvent?.outcome}</Text>
                </div>
              </Card>
            </Col>
            <Col span={12}>
              <Card title="进化后事件" size="small">
                <div>
                  <Title level={5}>{evolvedEvent?.title || '优化后的事件标题'}</Title>
                  <Text>{evolvedEvent?.description || '优化后的事件描述...'}</Text>
                  <Divider />
                  <Title level={5}>优化后的事件结果</Title>
                  <Text>{evolvedEvent?.outcome || '优化后的事件结果...'}</Text>
                </div>
              </Card>
            </Col>
          </Row>
        </div>
      </Modal>

      {/* 进化历史模态框 */}
      <Modal
        title="事件进化历史"
        open={showEvolutionHistoryModal}
        onCancel={() => setShowEvolutionHistoryModal(false)}
        footer={[
          <Button key="close" onClick={() => setShowEvolutionHistoryModal(false)}>
            关闭
          </Button>
        ]}
        width={800}
      >
        <List
          dataSource={currentEvolutionHistory}
          renderItem={(item) => (
            <List.Item>
              <List.Item.Meta
                title={`进化 #${item.id}`}
                description={
                  <div>
                    <Text>状态: <Tag color={item.status === 'accepted' ? 'green' : item.status === 'rejected' ? 'red' : 'orange'}>{item.status}</Tag></Text>
                    <br />
                    <Text type="secondary">评分质量: {item.score_quality}/10</Text>
                    <br />
                    <Text type="secondary">创建时间: {new Date(item.created_at).toLocaleString()}</Text>
                  </div>
                }
              />
            </List.Item>
          )}
        />
      </Modal>

      {/* 事件详情弹窗 */}
      <Modal
        title="事件详情"
        open={showEventDetailModal}
        onCancel={() => setShowEventDetailModal(false)}
        footer={[
          <Button key="close" onClick={() => setShowEventDetailModal(false)}>
            关闭
          </Button>
        ]}
        width={800}
      >
        {eventDetail && (
          <div>
            {/* 版本标识 */}
            <Alert
              message={eventDetail.is_evolved ? 
                `当前显示第 ${eventDetail.evolution_count + 1} 版（最新进化版本）` : 
                '当前显示原始版本'
              }
              type={eventDetail.is_evolved ? "success" : "info"}
              showIcon
              style={{ marginBottom: 16 }}
            />

            {/* 事件内容 */}
            <Card title={eventDetail.event.title}>
              <Text>{eventDetail.event.description}</Text>
              <Divider />
              <Title level={5}>事件结果</Title>
              <Text>{eventDetail.event.outcome}</Text>
            </Card>

            {/* 操作按钮 */}
            <div style={{ marginTop: 16, textAlign: 'center' }}>
              <Button 
                onClick={() => fetchEvolutionHistory(eventDetail.original_event_id)}
                icon={<DiffOutlined />}
              >
                查看进化历史
              </Button>
            </div>
          </div>
        )}
      </Modal>

      {/* 进化对比弹窗 */}
      <Modal
        title="进化对比"
        open={showEvolutionCompareModal}
        onCancel={() => setShowEvolutionCompareModal(false)}
        footer={[
          <Button key="close" onClick={() => setShowEvolutionCompareModal(false)}>
            关闭
          </Button>
        ]}
        width={1200}
      >
        {evolutionHistory && evolutionHistory.can_compare && (
          <div>
            <Alert
              message={`共 ${evolutionHistory.total_versions} 个版本，显示最新版本与上一版本的对比`}
              type="info"
              showIcon
              style={{ marginBottom: 16 }}
            />
            
            <Row gutter={16}>
              <Col span={12}>
                <Card title={`版本 ${evolutionHistory.previous_version?.metadata?.version || 0} ${evolutionHistory.previous_version?.metadata?.is_original ? '(原始)' : '(进化)'}`}>
                  <Title level={5}>{evolutionHistory.previous_version?.title}</Title>
                  <Text>{evolutionHistory.previous_version?.description}</Text>
                  <Divider />
                  <Title level={5}>事件结果</Title>
                  <Text>{evolutionHistory.previous_version?.outcome}</Text>
                  {evolutionHistory.previous_version?.metadata?.evolution_reason && (
                    <>
                      <Divider />
                      <Title level={5}>进化原因</Title>
                      <Text type="secondary">{evolutionHistory.previous_version.metadata.evolution_reason}</Text>
                    </>
                  )}
                </Card>
              </Col>
              <Col span={12}>
                <Card title={`版本 ${evolutionHistory.latest_version?.metadata?.version || 0} ${evolutionHistory.latest_version?.metadata?.is_original ? '(原始)' : '(进化)'}`}>
                  <Title level={5}>{evolutionHistory.latest_version?.title}</Title>
                  <Text>{evolutionHistory.latest_version?.description}</Text>
                  <Divider />
                  <Title level={5}>事件结果</Title>
                  <Text>{evolutionHistory.latest_version?.outcome}</Text>
                  {evolutionHistory.latest_version?.metadata?.evolution_reason && (
                    <>
                      <Divider />
                      <Title level={5}>进化原因</Title>
                      <Text type="secondary">{evolutionHistory.latest_version.metadata.evolution_reason}</Text>
                    </>
                  )}
                </Card>
              </Col>
            </Row>
          </div>
        )}
        
        {evolutionHistory && !evolutionHistory.can_compare && (
          <Empty
            description="该事件暂无进化历史，无法进行对比"
            image={Empty.PRESENTED_IMAGE_SIMPLE}
          />
        )}
      </Modal>
    </div>
  );
};

export default Events;