def process_message(message):
    if message['type'] == 'link' or message['type'] == 'unlink' or message['type'] == 'event':
        # { 'type':'update_entity', 'analyzer':'' } # analyzer가 존재하지 않을 경우 analyzer을 전부 찾아서 메시지큐에 등록
        # 이벤트가 추가된 경우에는 단순한데 이벤트 추가를 알림
        # 문제는 링크랑 언링크가 변경된 경우
        # 만약 링크가 된 경우 해당 링크된 시점부터 언링크 발견시까지... add 처리
        # 언링크 된 경우 언링크된 시점부터 다음 링크 시점까지... delete 처리

        # 링크/언링크 같은 경우 현재 해당 엔티티의 현재 시간 이후의 모든 이벤트를 update 시키는 방식으로 처리해야 할듯
        # 이벤트 추가시
        #  해당 이벤트가 참조되는 분석기를 콜! (추가로)
        #  변경의 경우도 삭제후 추가니까 ㅇㅇ

        from jobserver.process_event_message import process_event_message
        process_event_message(message)

        if message['type'] == 'event':
            from jobserver.group_mapping import notify_update_entity
            notify_update_entity(message['entity']['kind'], message['entity']['id'], message['log_key'])
        else:
            from jobserver.group_mapping import notify_update_entity_change_links
            notify_update_entity_change_links(message['service']['id'],
                                              message['entity']['kind'], message['entity']['id'],
                                              message['timestamp'])

    elif message['type'] == 'update_entity':
        # input 관리 서버에서 찾아서 없으면 그냥 종료하고 만약 발견된 경우
        # 그룹 탐색 (만약 이미 해당 이벤트가 다른 그룹인 경우 제거)
        # 그룹 인풋에 데이터 쓰기
        # log_key
        from jobserver.group_mapping import update_entity
        update_entity(message)
    elif message['type'] == 'update_analyzer_group':
        from jobserver.group_reduce import process_analyzer_group
        process_analyzer_group(message)

