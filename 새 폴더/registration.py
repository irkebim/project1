import inspect
import bpy
from typing import List, Tuple, Any, Dict, Type, Set, Optional

# 등록 데이터 저장
_classes = []
_properties = []
_modules = {}
_verbose = True  # 항상 로그 출력

def initialize(modules: Dict[str, Any], verbose: bool = True):
    """모듈 맵 및 클래스/속성 초기화"""
    global _modules, _classes, _properties, _verbose
    _modules = modules
    _classes = []
    _properties = []
    _verbose = verbose
    
    print("Registration: Initializing with", len(modules), "modules")
    
    # 모든 모듈에서 클래스와 속성 수집
    collect_from_all_modules()
    
    print(f"Registration: Collected {len(_classes)} classes and {len(_properties)} properties")

def collect_from_all_modules():
    """모든 모듈에서 클래스 및 속성 수집"""
    global _modules, _classes, _properties
    
    for name, module in _modules.items():
        if module is None:
            print(f"Module is None: {name}")
            continue
            
        # 클래스 수집 (자동 검색)
        for obj_name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and hasattr(obj, 'bl_rna') and not obj_name.startswith("_"):
                # 내장 클래스는 등록하지 않음 (AddonPreferences 등)
                if obj.__module__.startswith("bpy.types"):
                    print(f"Skipping built-in class: {obj.__name__}")
                    continue
                    
                if obj not in _classes:  # 중복 방지
                    _classes.append(obj)
                    if _verbose:
                        print(f"Added class: {obj.__name__} from {name}")
        
        # 속성 수집 (Property_ 접두사 검색)
        for attr_name in dir(module):
            if attr_name.startswith("Property_"):
                parts = attr_name.split("_", 2)  # Property_Owner_PropertyName
                if len(parts) >= 3:
                    owner_name = parts[1]
                    if hasattr(bpy.types, owner_name):
                        owner = getattr(bpy.types, owner_name)
                        prop_name = parts[2]
                        prop_value = getattr(module, attr_name)
                        
                        # 중복 방지
                        for existing_owner, existing_name, _ in _properties:
                            if existing_owner == owner and existing_name == prop_name:
                                print(f"Duplicate property found: {owner_name}.{prop_name}")
                                break
                        else:
                            _properties.append((owner, prop_name, prop_value))
                            if _verbose:
                                print(f"Added property: {owner_name}.{prop_name} from {name}")

def sort_classes(classes: List[Type]) -> List[Type]:
    """클래스를 적절한 등록 순서로 정렬"""
    panels = []
    operators = []
    prefs = []
    others = []
    
    for cls in classes:
        if cls is None:
            print("Warning: None found in classes list")
            continue
            
        try:
            if issubclass(cls, bpy.types.Panel):
                panels.append(cls)
            elif issubclass(cls, bpy.types.Operator):
                operators.append(cls)
            elif issubclass(cls, bpy.types.AddonPreferences):
                prefs.append(cls)
            else:
                others.append(cls)
        except TypeError:
            # 클래스가 아닌 경우 무시
            print(f"TypeError when checking {cls} - not a class")
            continue
    
    # 연산자 -> 기타 -> 설정 -> 패널 순으로 등록
    return operators + others + prefs + panels

def register_class(cls: Type) -> bool:
    """단일 클래스 등록 (안전하게)"""
    try:
        # 이미 등록된 클래스인지 확인 (중복 등록 방지)
        if hasattr(bpy.types, cls.__name__):
            print(f"Class already registered: {cls.__name__}")
            return True
            
        bpy.utils.register_class(cls)
        print(f"✓ Registered class: {cls.__name__}")
        return True
    except Exception as e:
        error_msg = str(e)
        # AddonPreferences 관련 에러는 무시 (일반적인 동작)
        if "AddonPreferences" in error_msg and "already registered" in error_msg:
            print(f"AddonPreferences registration info: {error_msg}")
            return True
            
        print(f"✗ Error registering {cls.__name__}: {e}")
        return False

def unregister_class(cls: Type) -> bool:
    """단일 클래스 등록 해제 (안전하게)"""
    try:
        bpy.utils.unregister_class(cls)
        print(f"✓ Unregistered class: {cls.__name__}")
        return True
    except Exception as e:
        error_msg = str(e)
        # AddonPreferences 관련 에러는 무시 (일반적인 동작)
        if "AddonPreferences" in error_msg and "built-in class" in error_msg:
            print(f"AddonPreferences unregistration info: {error_msg}")
            return True
            
        print(f"✗ Error unregistering {cls.__name__}: {e}")
        return False

def register_property(owner: Type, name: str, value: Any) -> bool:
    """단일 속성 등록 (안전하게)"""
    try:
        # 이미 존재하면 제거
        if hasattr(owner, name):
            print(f"Property already exists: {owner.__name__}.{name}, will be replaced")
            delattr(owner, name)
        
        # 새로 설정
        setattr(owner, name, value)
        print(f"✓ Registered property: {owner.__name__}.{name}")
        return True
    except Exception as e:
        print(f"✗ Error registering property {owner.__name__}.{name}: {e}")
        return False

def unregister_property(owner: Type, name: str) -> bool:
    """단일 속성 등록 해제 (안전하게)"""
    try:
        if hasattr(owner, name):
            delattr(owner, name)
            print(f"✓ Unregistered property: {owner.__name__}.{name}")
            return True
        else:
            print(f"Property not found for unregistration: {owner.__name__}.{name}")
    except Exception as e:
        print(f"✗ Error unregistering property {owner.__name__}.{name}: {e}")
    return False

def register_all():
    """모든 클래스 및 속성 등록"""
    # 클래스 정렬
    sorted_classes = sort_classes(_classes)
    print(f"Registering {len(sorted_classes)} classes")
    
    # 클래스 등록
    for cls in sorted_classes:
        register_class(cls)
    
    # 속성 등록
    print(f"Registering {len(_properties)} properties")
    for owner, name, value in _properties:
        register_property(owner, name, value)

def unregister_all():
    """모든 클래스 및 속성 등록 해제"""
    # 속성 등록 해제 (등록의 역순)
    print(f"Unregistering {len(_properties)} properties")
    for owner, name, _ in reversed(_properties):
        unregister_property(owner, name)
    
    # 클래스 등록 해제 (등록의 역순)
    sorted_classes = sort_classes(_classes)
    print(f"Unregistering {len(sorted_classes)} classes")
    for cls in reversed(sorted_classes):
        unregister_class(cls)