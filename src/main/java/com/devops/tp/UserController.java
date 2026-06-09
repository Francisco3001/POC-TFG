package com.devops.tp;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;

import jakarta.persistence.EntityManager;
import jakarta.persistence.PersistenceContext;

import java.util.List;

@RestController
@RequestMapping("/users")
public class UserController {

    @Autowired
    private UserRepository userRepository;
    @PersistenceContext
    private EntityManager entityManager;

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public User createUser(@RequestBody User user) {
        return userRepository.save(user);
    }

    @GetMapping("/search")
    public List<?> search(@RequestParam String name) {

        String query = "SELECT * FROM users WHERE name = '" + name + "'";

        return entityManager.createNativeQuery(query).getResultList();
    }


    @GetMapping("/search2")
    public List<?> search2(@RequestParam String name) {

        String query = "SELECT * FROM users WHERE name = '" + name + "'";

        return entityManager.createNativeQuery(query).getResultList();
        //asdasd
    }

    @GetMapping
    public List<User> getUsers() {
        return userRepository.findAll();
    }
}
